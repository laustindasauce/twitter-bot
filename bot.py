""" If you want a visual plot for the sentiment analysis then you need to un-comment plt and sns imports """
import tweepy
from textblob import TextBlob
import pandas as pd
# import matplotlib as plt
import numpy as np
import redis
# import seaborn as sns
import schedule
import time
import re
import os


consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
key = os.getenv("KEY")
secret = os.getenv("SECRET")

client = redis.Redis(host="10.10.10.1", port=6379,
                     password=os.getenv("REDIS_PASS"))
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
auth.secure = True
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

tweets = api.mentions_timeline()


def read_last_seen():
    last_seen_id = int(client.get('last_seen_id'))
    return last_seen_id


def store_last_seen(last_seen_id):
    client.set('last_seen_id', str(last_seen_id))
    return


def reply():
    tweets = api.mentions_timeline(
        read_last_seen(), tweet_mode='extended')
    for tweet in reversed(tweets):
        try:
            username = tweet.user.screen_name
            if username != "CalendarKy" and tweet.full_text[:11] != "@CalendarKy":
                print("Replied to - " + username +
                      " - " + tweet.full_text)
                api.update_status("@" + username +
                                    " Hello, " + username + ", just a moment. " + 
                                    "@CalendarKy could you please help me out?", tweet.id)
            else:
                print("Favorited " + username +
                  " - " + tweet.full_text)
            api.create_favorite(tweet.id)
            store_last_seen(tweet.id)
        except tweepy.TweepError as e:
            store_last_seen(tweet.id)
            print(e.reason)
            time.sleep(2)


def searchBot():
    tweets = tweepy.Cursor(api.search, "#bullmarket").items(2)
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


def searchBot2():
    tweets = tweepy.Cursor(api.search, "stonks").items(20)
    print("Running second search.")
    print(time.ctime())
    i = 0
    for tweet in tweets:
        try:
            i += 1
            api.create_favorite(tweet.id)
            if i % 10 == 0:
                tweet.retweet()
                print("Retweet 2 done!")
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)


def searchBot3():
    tweets = tweepy.Cursor(api.search, "stock market").items(300)
    print("Running third search.")
    print(time.ctime())
    i = 0
    for tweet in tweets:
        try:
            api.create_favorite(tweet.id)
            time.sleep(2)
            i += 1
            if i % 20 == 0:
                print(f"Favorited {i} stock market tweets")
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)


def tweet_sentiment():
    client = redis.Redis(host="10.10.10.1", port=6379,
                         password=os.getenv("REDIS_PASS"))
    sentiment = client.get('twit_bot').decode("utf-8")
    status = f"I am currently {sentiment} the stock market."
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
    retweet_filter = '-filter:retweets'
    q = searchQuery+retweet_filter
    tweetCount = 0
    max_id = -1
    tweetsPerQry = 100
    redisDataBase = 'tweets_scraped'
    sinceId = None
    while tweetCount < (maxTweets-50):
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(
                        q=q, lang="en", count=tweetsPerQry, tweet_mode='extended')
                else:
                    new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                            since_id=sinceId, tweet_mode='extended')
            else:
                if (not sinceId):
                    new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                            max_id=str(max_id - 1), tweet_mode='extended')
                else:
                    new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            since_id=sinceId, tweet_mode='extended')
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                client.sadd(redisDataBase, (str(tweet.full_text.replace(
                    '\n', '').encode("utf-8"))+"\n"))
            tweetCount += len(new_tweets)
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break
    print(f"Downloaded {tweetCount} tweets; Saved to {redisDataBase}")


def clean(tweet):
    tweet = re.sub(r'^RT[\s]+', '', tweet)
    tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)
    tweet = re.sub(r'#', '', tweet)
    tweet = re.sub(r'@[A-Za-z0–9]+', '', tweet)
    return tweet


def read_tweets(redis_set):
    f = client.smembers(redis_set)
    tweets = [clean(sentence.decode("utf-8").strip()) for sentence in f]
    return tweets


def polarity(x): return TextBlob(x).sentiment.polarity


def subjectivity(x): return TextBlob(x).sentiment.subjectivity


def run_scraper():
    redisDataBase = "tweets_scraped"
    scrape_twitter(3000, 'stock market', redisDataBase)
    f = read_tweets(redisDataBase)
    tweet_polarity = np.zeros(client.scard(redisDataBase))
    tweet_subjectivity = np.zeros(client.scard(redisDataBase))
    bullish_count = 0
    bearish_count = 0
    for idx, tweet in enumerate(f):
        tweet_polarity[idx] = polarity(tweet)
        tweet_subjectivity[idx] = subjectivity(tweet)
        if tweet_polarity[idx] > 0.15:
            bullish_count += 1
        elif tweet_polarity[idx] < 0.00:
            bearish_count += 1
    # sns.scatterplot(tweet_polarity,  # X-axis
    #                 tweet_subjectivity,  # Y-axis
    #                 s=100)
    sentiment = (bullish_count) - bearish_count
    print(f"Bullish count is {bullish_count}")
    print(f"Bearish count is {bearish_count}")
    print(f"Sentiment count is {sentiment}")
    to_string = "null"
    if sentiment > 30:
        to_string = f"Twitter sentiment of the stock market is bullish with a reading of {sentiment}."
        current_high = int(client.get('highest_sentiment'))
        if sentiment > current_high:
            client.set('highest_sentiment', str(sentiment))
            to_string = f"{to_string} This is the highest reading to date."
    elif sentiment > -5:
        to_string = f"Twitter sentiment of the stock market is nuetral with a reading of {sentiment}."
    else:
        to_string = f"Twitter sentiment of the stock market is bearish with a reading of {sentiment}."
        current_low = int(client.get('lowest_sentiment'))
        if sentiment < current_low:
            client.set('lowest_sentiment', str(sentiment))
            to_string = f"{to_string} This is the lowest reading to date."
    print(to_string)
    api.update_status(to_string)
    # plt.title("Sentiment Analysis", fontsize=20)
    # plt.xlabel('← Negative — — — — — — Positive →', fontsize=15)
    # plt.ylabel('← Facts — — — — — — — Opinions →', fontsize=15)
    # plt.tight_layout()
    # plt.show()


# This is trying to get followers that will be active and interested in my content
def auto_follow():
    query = "stock market"
    print(f"Following users who have tweeted about the {query}")
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(50)
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


# This is to purely try to get my follower count up
def auto_follow2():
    query = "ifb"
    print(f"Following users who have tweeted about the {query}")
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(50)
    num_followed = 0
    for tweet in search:
        if tweet.user.followers_count > 3000:
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
    query = "follow back"
    print(f"Following users who have tweeted about the {query}")
    # Switch up the query
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(50)
    for tweet in search:
        if tweet.user.followers_count > 3000:
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
    total_followers = client.scard('followers_thanked')
    followers_thanked = []
    followers = []
    for follower in list(client.smembers('followers_thanked')):
        followers_thanked.append(follower.decode("utf-8"))
    followers_thanked = set(followers_thanked)
    for follower in tweepy.Cursor(api.followers).items(100):
        followers.append(str(follower.id))
        #follower has a long list of possible things to see.. kinda neat
        if not follower.following:
            try:
                follower.follow()
                time.sleep(3)
                # Moved this print statement so that if there is an error we don't print 
                print(f"Following {follower.name}")
            except tweepy.TweepError as e:
                """ Ignores error that we've already tried to follow this person
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
            to_string = "Thanks for the follow! Also, follow @CalendarKy for a follow back and more market information!"
            api.send_direct_message(follower, to_string)
            client.sadd('followers_thanked', str(follower))
        new_total_followers = client.scard('followers_thanked')
        total_followers = new_total_followers - total_followers
        print(f"Tendie Intern has {total_followers} new followers. Total of {new_total_followers} followers.")


print(time.ctime())
schedule.every().week.do(unfollow)
schedule.every(3).days.at("04:01").do(auto_follow2)
schedule.every().thursday.at("11:37").do(unfollow)
schedule.every().day.at("13:26").do(auto_follow)
schedule.every().day.at("15:13").do(tweet_sentiment)
schedule.every().day.at("09:17").do(searchBot)
schedule.every().day.at("12:12").do(searchBot2)
schedule.every().day.at("17:03").do(searchBot3)
schedule.every().day.at("09:06").do(searchBot3)
schedule.every(15).minutes.do(reply)
schedule.every(7).hours.do(run_scraper)
schedule.every(20).minutes.do(thank_new_followers)


while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except tweepy.TweepError as e:
        print(e.reason)
        time.sleep(1)
