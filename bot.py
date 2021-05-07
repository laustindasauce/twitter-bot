import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import redis
import seaborn as sns
import schedule
from textblob import TextBlob
import time
import tweepy


""" Need to sign up for a developer twitter account to get these check README """
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
key = os.getenv("KEY")
secret = os.getenv("SECRET")


""" Download Redis and have a server running check README """

### GOOGLE CLOUD REDIS SERVER or KUBERNETES APPLICATION ###
client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=6379,
    db=os.getenv("DATABASE"),  # 0-15 default is 0
    password=os.getenv("REDIS_PASS"),
)

### LOCAL REDIS SERVER ###
client = redis.Redis(
    host="127.0.0.1",
    port=6379, # Default
    db=1, # 0-15 default is 0
    password="IF YOU SET ONE"
)


### TWEEPY SETUP ###
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
auth.secure = True
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


""" Global variable for our png file path """
png_file = "/tmp/plot.png"


def read_last_seen():
    last_seen_id = int(client.get("last_seen_id"))
    return last_seen_id


def store_last_seen(last_seen_id):
    client.set("last_seen_id", str(last_seen_id))
    return


def reply():
    tweets = api.mentions_timeline(read_last_seen(), tweet_mode="extended")
    for tweet in reversed(tweets):
        try:
            username = tweet.user.screen_name

            print("Replied to - " + username + " - " + tweet.full_text)
            api.update_status(
                "@" + username + " Hello, " + username + ", this is an auto reply :)",
                tweet.id,
            )

            print("Favorited " + username + " - " + tweet.full_text)
            api.create_favorite(tweet.id)
            store_last_seen(tweet.id)
        except tweepy.TweepError as e:
            store_last_seen(tweet.id)
            print(e.reason)
            time.sleep(2)


def get_dms():
    last_seen = int(client.get("dm_seen"))
    messages = api.list_direct_messages(last_seen)
    for message in reversed(messages):
        sender_id = message.message_create["sender_id"]
        # Don't worry about DM's that you sent
        if sender_id != "Your user id":
            text = message.message_create["message_data"]["text"]
            print(text)
            reply_dm(sender_id)
        last_seen = message.id
    # Update our last seen dm ID
    client.set("dm_seen", str(last_seen))


def reply_dm(sender_id):
    to_string = "Example auto-reply"
    api.send_direct_message(sender_id, to_string)
    print("Sent reply dm")


def searchBot():
    tweets = tweepy.Cursor(api.search, "whatever you want here").items(2)
    print("Running first search.")
    print(time.ctime())
    for tweet in tweets:
        try:
            tweet.retweet()
            print("Retweet done!")
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)


def tweet_sentiment():
    sentiment = client.get("twit_bot").decode("utf-8")
    status = f"The sentiment for 'Example' is {sentiment}."
    print(status)
    print("Updating our status to our current sentiment.")
    api.update_status(status)


def follow_followers():
    for follower in tweepy.Cursor(api.followers).items():
        if not follower.following:
            print(f"Following {follower.name}")
            follower.follow()
            time.sleep(2)


def scrape_twitter(maxTweets, searchQuery, redisDataBase):
    client.delete(redisDataBase)
    print(f"Downloading max {maxTweets} tweets")
    retweet_filter = "-filter:retweets"
    q = searchQuery + retweet_filter
    tweetCount = 0
    max_id = -1
    tweetsPerQry = 100
    redisDataBase = "tweets_scraped"
    sinceId = None
    while tweetCount < (maxTweets - 50):
        try:
            if max_id <= 0:
                if not sinceId:
                    new_tweets = api.search(
                        q=q, lang="en", count=tweetsPerQry, tweet_mode="extended"
                    )
                else:
                    new_tweets = api.search(
                        q=q,
                        lang="en",
                        count=tweetsPerQry,
                        since_id=sinceId,
                        tweet_mode="extended",
                    )
            else:
                if not sinceId:
                    new_tweets = api.search(
                        q=q,
                        lang="en",
                        count=tweetsPerQry,
                        max_id=str(max_id - 1),
                        tweet_mode="extended",
                    )
                else:
                    new_tweets = api.search(
                        q=q,
                        lang="en",
                        count=tweetsPerQry,
                        max_id=str(max_id - 1),
                        since_id=sinceId,
                        tweet_mode="extended",
                    )
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                client.sadd(
                    redisDataBase,
                    (str(tweet.full_text.replace("\n", "").encode("utf-8")) + "\n"),
                )
            tweetCount += len(new_tweets)
            max_id = new_tweets[-1].id

        except tweepy.TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break
    print(f"Downloaded {tweetCount} tweets; Saved to {redisDataBase}")


def clean(tweet):
    tweet = re.sub(r"^RT[\s]+", "", tweet)
    tweet = re.sub(r"https?:\/\/.*[\r\n]*", "", tweet)
    tweet = re.sub(r"#", "", tweet)
    tweet = re.sub(r"@[A-Za-z0–9]+", "", tweet)
    return tweet


def read_tweets(redis_set):
    f = client.smembers(redis_set)
    tweets = [clean(sentence.decode("utf-8").strip()) for sentence in f]
    return tweets


def polarity(x):
    return TextBlob(x).sentiment.polarity


def subjectivity(x):
    return TextBlob(x).sentiment.subjectivity


def run_scraper():
    redisDataBase = "tweets_scraped"
    scrape_twitter(3000, "Example", redisDataBase)
    f = read_tweets(redisDataBase)
    tweet_polarity = np.zeros(client.scard(redisDataBase))
    tweet_subjectivity = np.zeros(client.scard(redisDataBase))
    positive_count = 0
    negative_count = 0
    for idx, tweet in enumerate(f):
        tweet_polarity[idx] = polarity(tweet)
        tweet_subjectivity[idx] = subjectivity(tweet)
        # Filter out the opinionated tweets by having subjectivity < 0.5
        if tweet_polarity[idx] > 0.00 and tweet_subjectivity[idx] < 0.5:
            positive_count += 1
        elif tweet_polarity[idx] < 0.00 and tweet_subjectivity[idx] < 0.5:
            negative_count += 1
    sns.scatterplot(tweet_polarity, tweet_subjectivity, s=100)  # X-axis  # Y-axis
    sentiment = (positive_count) - negative_count
    print(f"Positive count is {positive_count}")
    print(f"Negative count is {negative_count}")
    print(f"Sentiment count is {sentiment}")
    to_string = "null"
    if sentiment > 0:
        to_string = (
            f"Twitter sentiment of 'Example' is positive with a reading of {sentiment}."
        )
        current_high = int(client.get("highest_sentiment"))
        if sentiment > current_high:
            client.set("highest_sentiment", str(sentiment))
            to_string = f"{to_string} This is the highest reading to date."
    elif sentiment == 0:
        to_string = (
            f"Twitter sentiment of 'Example' is nuetral with a reading of {sentiment}."
        )
    else:
        to_string = (
            f"Twitter sentiment of 'Example' is negative with a reading of {sentiment}."
        )
        current_low = int(client.get("lowest_sentiment"))
        if sentiment < current_low:
            client.set("lowest_sentiment", str(sentiment))
            to_string = f"{to_string} This is the lowest reading to date."
    print(to_string)
    plt.title("Sentiment Analysis", fontsize=20)
    plt.xlabel("← Negative — — — — — — Positive →", fontsize=15)
    plt.ylabel("← Facts — — — — — — — Opinions →", fontsize=15)
    plt.tight_layout()
    plt.savefig(png_file)
    api.update_with_media(png_file, to_string)
    # plt.show()


# This is trying to get followers that will be active and interested in my content
def auto_follow():
    query = "Whatever you want here"
    print(f"Following users who have tweeted about the {query}")
    search = tweepy.Cursor(api.search, q=query, result_type="recent", lang="en").items(50)
    num_followed = 0
    for tweet in search:
        if tweet.user.followers_count > 2000:
            continue
        try:
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)
        try:
            api.create_friendship(tweet.user.id)
            time.sleep(2)
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 160":
                print(e.reason)
            time.sleep(2)
    print(f"Now following {num_followed} more users.")


def unfollow():
    print("running unfollow function")
    friendNames, followNames = [], []
    try:
        for friend in tweepy.Cursor(api.friends).items(200):
            if friend.followers_count < 5000:
                friendNames.append(friend.screen_name)
                time.sleep(2)

        for follower in tweepy.Cursor(api.followers).items(200):
            followNames.append(follower.screen_name)
            time.sleep(2)
    except tweepy.TweepError as e:
        print(e.reason)
        time.sleep(2)
    friendset = set(friendNames)
    followset = set(followNames)
    not_fback = friendset.difference(followset)
    for not_following in not_fback:
        try:
            api.destroy_friendship(not_following)
            print(f"Unfollowing: {not_following}")
            time.sleep(3)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)


def thank_new_followers():
    total_followers = client.scard("followers_thanked")
    followers_thanked = []
    followers = []
    for follower in list(client.smembers("followers_thanked")):
        followers_thanked.append(follower.decode("utf-8"))
    followers_thanked = set(followers_thanked)
    for follower in tweepy.Cursor(api.followers).items(100):
        followers.append(str(follower.id))
        # follower has a long list of possible things to see.. kinda neat
        if not follower.following:
            try:
                follower.follow()
                time.sleep(3)
                # Moved this print statement so that if there is an error we don't print
                print(f"Following {follower.name}")
            except tweepy.TweepError as e:
                """Ignores error that we've already tried to follow this person
                The reason we're ignoring this error is because if someone is private
                we will keep trying to follow them until they accept our follow.
                """
                if e.reason[:13] != "[{'code': 160":
                    print(e.reason)
                time.sleep(2)
    followers_set = set(followers)
    new_followers = followers_set.difference(followers_thanked)
    if new_followers:
        print("Thanking new followers.")
        for follower in new_followers:
            to_string = "Thanks for the follow!"
            api.send_direct_message(follower, to_string)
            client.sadd("followers_thanked", str(follower))
        new_total_followers = client.scard("followers_thanked")
        total_followers = new_total_followers - total_followers
        print(f"{total_followers} new followers. Total of {new_total_followers} followers.")


print(time.ctime())

schedule.every().week.do(unfollow)
schedule.every().thursday.at("11:35").do(unfollow)
schedule.every().day.at("13:26").do(auto_follow)
schedule.every().day.at("15:13").do(tweet_sentiment)
schedule.every().day.at("09:17").do(searchBot)
schedule.every(15).minutes.do(reply)
schedule.every(5).hours.do(run_scraper)
schedule.every(19).minutes.do(thank_new_followers)


while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except tweepy.TweepError as e:
        print(e.reason)
        time.sleep(1)
