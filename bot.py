import tweepy
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import redis
import seaborn as sns
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

png_file = "/tmp/plot.png"

def read_last_seen():
    last_seen_id = int(client.get('last_seen_id'))
    return last_seen_id


def store_last_seen(last_seen_id):
    client.set('last_seen_id', str(last_seen_id))
    return


def reply():
    print("Running reply()")
    tweets = api.mentions_timeline(
        read_last_seen(), tweet_mode='extended')
    for tweet in reversed(tweets):
        try:
            username = tweet.user.screen_name
            if username != "CalendarKy" and username != "statutorywheel" and tweet.full_text[:11] != "@CalendarKy" \
                and tweet.full_text[:11] != "@statutorywheel" and tweet.full_text[:17] != "@InternTendie and":
                print("Replied to - " + username +
                      " - " + tweet.full_text)
                api.update_status("@" + username +
                                    " Hello, " + username + ", just a moment. " + 
                                    "@CalendarKy @statutorywheel, can I please get some help?", tweet.id)
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
    print("Running #python search.")
    tweets = tweepy.Cursor(api.search, "#python").items(20)
    # print("Running first search.")
    print(time.ctime())
    i = 0
    for tweet in tweets:
        i += 1
        try:
            # print("Retweet done!")
            if i % 50 == 0:
                # tweet.retweet()
                print(f"Favorited {i} #python tweets.")
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            elif e.reason[:13] == "[{'code': 283" or e.reason[:13] == "[{'code': 429":
                print("Malicious activity suspected. Ending searchBot.")
                return
            else:
                print(e.reason)
            time.sleep(2)


def searchBot2():
    print("Running javascript search.")
    tweets = tweepy.Cursor(api.search, "javascript").items(10)
    # print("Running second search.")
    print(time.ctime())
    i = 0
    for tweet in tweets:
        try:
            i += 1
            if i % 25 == 0:
                # tweet.retweet()
                print(f"Favorited {i} javascript tweets.")
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            elif e.reason[:13] == "[{'code': 283" or e.reason[:13] == "[{'code': 429":
                print("Malicious activity suspected. Ending searchBot2.")
                return
            else:
                print(e.reason)
            time.sleep(2)


def searchBot3():
    print("Running algorithm search.")
    tweets = tweepy.Cursor(api.search, "algorithm").items(10)
    # print("Running third search.")
    print(time.ctime())
    i = 0
    for tweet in tweets:
        try:
            i += 1
            if i % 20 == 0:
                print(f"Favorited {i} algorithm tweets")
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            elif e.reason[:13] == "[{'code': 283" or e.reason[:13] == "[{'code': 429":
                print("Malicious activity suspected. Ending searchBot3.")
                return
            else:
                print(e.reason)
            time.sleep(2)


def ifb_bot():
    print("Running ifb search.")
    tweets = tweepy.Cursor(api.search, "ifb").items(150)
    i = 0
    for tweet in tweets:
        i += 1
        try:
            if i % 50 == 0:
                print(f"Favorited {i} ifb tweets")
            api.create_favorite(tweet.id)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            elif e.reason[:13] == "[{'code': 283" or e.reason[:13] == "[{'code': 429":
                print("Malicious activity suspected. Ending ifb_bot.")
                return
            else:
                print(e.reason)
        time.sleep(4)


def tweet_sentiment():
    print("Running tweet_sentiment()")
    client = redis.Redis(host="10.10.10.1", port=6379,
                         password=os.getenv("REDIS_PASS"))
    sentiment = client.get('twit_bot').decode("utf-8")
    status = f"I am currently {sentiment} the stock market."
    print(status)
    api.update_status(status)


def scrape_twitter(maxTweets, searchQuery, redisDataBase):
    client.delete(redisDataBase)
    # print(f"Downloading max {maxTweets} tweets")
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
    # print(f"Downloaded {tweetCount} tweets; Saved to {redisDataBase}")


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
    print("Running data scraper.")
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
        if tweet_polarity[idx] > 0.15 and tweet_subjectivity[idx] < 0.5:
            bullish_count += 1
        elif tweet_polarity[idx] < 0.00 and tweet_subjectivity[idx] < 0.5:
            bearish_count += 1
    # sns.scatterplot(tweet_polarity,  # X-axis
    #                 tweet_subjectivity,  # Y-axis
                    # s=100)
    bullish_count -= 35
    sentiment = (bullish_count) - bearish_count
    # print(f"Bullish count is {bullish_count}")
    # print(f"Bearish count is {bearish_count}")
    # print(f"Sentiment count is {sentiment}")
    if sentiment > 5:
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
    # plt.savefig(png_file)
    # api.update_with_media(png_file, to_string)
    # plt.show()


# This is trying to get followers that will be active and interested in my content
def auto_follow():
    print("Running auto_follow()")
    query = "computer science"
    # print(f"Following users who have tweeted about the {query}")
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(10)
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
            time.sleep(5)
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429" or e.reason[:13] == "[{'code': 283":
                print(f"Now following {num_followed} more users.")
                print("Followed too many people... ending auto_follow")
                return
            else:
                print(e.reason)
            time.sleep(2)
    query = "programming"
    # print(f"Following users who have tweeted about the {query}")
    # Switch up the query
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(10)
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
            time.sleep(5)
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429" or e.reason[:13] == "[{'code': 283":
                print("Followed too many people... ending auto_follow")
                print(f"Now following {num_followed} more users.")
                return
            else:
                print(e.reason)
            time.sleep(2)
    print(f"Now following {num_followed} more users.")
    query = "python program"
    # print(f"Following users who have tweeted about the {query}")
    # Switch up the query
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(10)
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
            time.sleep(5)
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429" or e.reason[:13] == "[{'code': 283":
                print("Followed too many people... ending auto_follow")
                print(f"Now following {num_followed} more users.")
                return
            else:
                print(e.reason)
            time.sleep(2)
    print(f"Now following {num_followed} more users.")

# This is to purely try to get my follower count up
def auto_follow2():
    print("Running auto_follow2()")
    query = "ifb"
    # print(f"Following users who have tweeted about the {query}")
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(25)
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
            time.sleep(5)
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429" or e.reason[:13] == "[{'code': 283":
                print(f"Now following {num_followed} more users.")
                print("Followed too many people... ending auto_follow")
                return
            else:
                print(e.reason)
            time.sleep(2)
    query = "follow back"
    # print(f"Following users who have tweeted about the {query}")
    # Switch up the query
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(25)
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
            time.sleep(5)
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429" or e.reason[:13] == "[{'code': 283":
                print("Followed too many people... ending auto_follow")
                print(f"Now following {num_followed} more users.")
                return
            else:
                print(e.reason)
            time.sleep(2)
    print(f"Now following {num_followed} more users.")


def unfollow():
    print("Running unfollow()")
    friendNames, followNames = [], []
    try:
        for friend in tweepy.Cursor(api.friends).items(300):
            if friend.followers_count < 5000:
                friendNames.append(friend.screen_name)

        for follower in tweepy.Cursor(api.followers).items(300):
            followNames.append(follower.screen_name)

    except tweepy.TweepError as e:
        print(e.reason)
        time.sleep(2)
    friendset = set(friendNames)
    followset = set(followNames)
    not_fback = friendset.difference(followset)
    unfollow_count = 0
    for not_following in not_fback:
        try:
            unfollow_count += 1
            api.destroy_friendship(not_following)
        except tweepy.TweepError as e:
            print(e.reason)
        time.sleep(5)
    print(f"Unfollowed: {unfollow_count} losers.")


def thank_new_followers():
    print("Running thank_new_followers()")
    total_followers = client.scard('followers_thanked')
    followers_thanked = []
    followers = []
    for follower in list(client.smembers('followers_thanked')):
        followers_thanked.append(follower.decode("utf-8"))
    followers_thanked = set(followers_thanked)
    follow_count = 0
    limit = False
    for follower in tweepy.Cursor(api.followers).items(100):
        followers.append(str(follower.id))
        #follower has a long list of possible things to see.. kinda neat
        if not follower.following:
            try:
                follower.follow()
                follow_count += 1
                # Moved this print statement so that if there is an error we don't print 
                # print(f"Following {follower.name}")
            except tweepy.TweepError as e:
                """ Ignores error that we've already tried to follow this person
                    The reason we're ignoring this error is because if someone is private
                    we will keep trying to follow them until they accept our follow. Which 
                    will give the error of already pending request.
                """
                if e.reason[:13] == "[{'code': 160":
                    continue
                elif e.reason[:13] == "[{'code': 161" or e.reason[:13] == "[{'code': 429":
                    print("Following limit hit!!")
                    limit = True
                    break
                elif e.reason[:13] == "[{'code': 283":
                    print("Malicious activity suspected. Can't follow back right now.")
                    limit = True
                    break
                else:
                    print(e.reason)
            time.sleep(3)
    if follow_count > 0:
        print(f"Tendie followed back {follow_count} people.")
    followers_set = set(followers)
    new_followers = followers_set.difference(followers_thanked)
    if new_followers:
        # print("Thanking new followers.")
        trouble = False
        to_string = "Appreciate you following me! Check out my github if you're intereseted in programming! " + \
            "Also, if you'd like to create a twitter bot of your own, you can find how to do that there!\n" + \
            "Github: https://github.com/abspen1"
        if limit:
            to_string = f"{to_string}\nSorry, I've hit a following limit and will follow you back ASAP!"
        for follower in new_followers:
            if not trouble:
                try:
                    client.sadd('followers_thanked', str(follower))
                    api.send_direct_message(follower, to_string)
                except tweepy.TweepError as e:
                    if e.reason[:13] == "[{'code': 226" or e.reason[:13] == "[{'code': 429":
                        print("They think this is spam...")
                        trouble = True
                    else:
                        print(e)
                time.sleep(3)
            else:
                try:
                    client.sadd('followers_thanked', str(follower))
                except tweepy.TweepError as e:                        
                    print(e)
        new_total_followers = client.scard('followers_thanked')
        total_followers = new_total_followers - total_followers
        print(f"Tendie Intern has {total_followers} new followers. Total of {new_total_followers} followers.")


def specific_favorite():
    client = redis.Redis(host="10.10.10.1", port=6379,
                         password=os.getenv("REDIS_PASS"))
    sinceId = 'ky_since_id'
    client.set(sinceId, '1285706104433979392')
    tweet_id = int(client.get(sinceId))
    tweets = api.home_timeline(since_id=tweet_id, include_rts=1, count=200)
    for tweet in reversed(tweets):
        client.set(sinceId, str(tweet.id))
        try:
            if tweet.user.screen_name == 'CalendarKy' or tweet.user.screen_name == 'statutorywheel':
                if str(tweet.text)[:1] != "@" and str(tweet.text)[:2] != "RT":
                    api.create_favorite(tweet.id)
                    # tweet.retweet()
                    # print(client.get(sinceId))
                    print(f"Favorited {tweet.user.screen_name}'s tweet.")
                    time.sleep(3)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(3)
        time.sleep(1)
        

print(time.ctime())
schedule.every().week.do(unfollow)
# schedule.every(3).days.at("09:01").do(auto_follow2)
schedule.every().thursday.at("03:37").do(unfollow)
# schedule.every().monday.at("03:37").do(unfollow)
schedule.every().day.at("13:26").do(auto_follow)
schedule.every().day.at("15:13").do(tweet_sentiment)
schedule.every().day.at("10:17").do(searchBot)
schedule.every().day.at("12:12").do(searchBot2)
schedule.every().day.at("17:07").do(searchBot3)
# schedule.every(4).hours.do(ifb_bot)
schedule.every(20).minutes.do(reply)
schedule.every(7).hours.do(run_scraper)
schedule.every(15).minutes.do(thank_new_followers)
schedule.every(7).minutes.do(specific_favorite)


while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except tweepy.TweepError as e:
        print(e.reason)
        print("We errored out.. going to sleep for 2 hours..")
        time.sleep(2*60*60)