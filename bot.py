import tweepy
import time
import schedule
import redis
import os

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
key = os.getenv("KEY")
secret = os.getenv("SECRET")

client = redis.Redis(host="10.10.10.1", port=6379,
                     password=os.getenv("REDIS_PASS"))
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

tweets = api.mentions_timeline()

FILE_NAME = 'last_seen.txt'


def read_last_seen(FILE_NAME):
    # file_read = open(FILE_NAME, 'r')
    # last_seen_id = int(file_read.read().strip())
    # file_read.close()
    last_seen_id = int(client.get('last_seen_id'))
    return last_seen_id


def store_last_seen(last_seen_id):
    # file_write = open(FILE_NAME, 'w')
    # file_write.write(str(last_seen_id))
    # file_write.close()
    client.set('last_seen_id', str(last_seen_id))
    return

#store_last_seen(FILE_NAME, '1194877411671724066')

def reply():
    print("Checking for any mentions")
    print(time.ctime())
    tweets = api.mentions_timeline(
        read_last_seen(FILE_NAME), tweet_mode='extended')
    for tweet in reversed(tweets):
        #if 'bullish' in tweet.full_text.lower():
        try:
            print("Replied to ID - " + str(tweet.id) + " - " + tweet.full_text)
            username = tweet.user.screen_name
            api.update_status("@" + tweet.user.screen_name +
                                " Hello, " + username + " I'm a bot idk why you're mentioning me.", tweet.id)
            #api.retweet(tweet.id)
            api.create_favorite(tweet.id)
            store_last_seen(tweet.id)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)

tweetNumber = 2

tweets = tweepy.Cursor(api.search, "#bullmarket").items(tweetNumber)


def searchBot():
    print("Running first search.")
    print(time.ctime())
    for tweet in tweets:
        try:
            tweet.retweet()
            print("Retweet done!")
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)

new_tweets = tweepy.Cursor(api.search, "bull gang").items(tweetNumber)


def searchBot2():
    print("Running second search.")
    print(time.ctime())
    for tweet in new_tweets:
        try:
            tweet.retweet()
            print("Retweet 2 done!")
            time.sleep(2)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)

newer_tweets = tweepy.Cursor(api.search, "#ddtg").items(tweetNumber)

def searchBot3():
    print("Running third search.")
    print(time.ctime())
    for tweet in newer_tweets:
        try:
            tweet.retweet()
            print("Retweeted ddtg!")
            time.sleep(2)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)
def tweet_sentiment():
    print(time.ctime())
    client = redis.Redis(host="10.10.10.1", port=6379,
                         password=os.getenv("REDIS_PASS"))
    sentiment = client.get('twit_bot').decode("utf-8")
    status = "I am currently {} the stock market.".format(sentiment)
    print(status)
    print("Updating our status to our current sentiment.")
    api.update_status(status)


def follow_followers(api):
    print("Retrieving and following followers")
    for follower in tweepy.Cursor(api.followers).items():
        if not follower.following:
            print(f"Following {follower.name}")
            follower.follow()


print(time.ctime())
schedule.every().day.at("15:15").do(tweet_sentiment)
schedule.every().day.at("09:15").do(searchBot)
schedule.every().day.at("12:15").do(searchBot2)
schedule.every().day.at("16:15").do(searchBot3)
schedule.every(10).minutes.do(reply)
schedule.every().hour.do(follow_followers)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except tweepy.TweepError as e:
        print(e.reason)
        time.sleep(1)
