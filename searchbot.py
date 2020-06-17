import tweepy
import time
import os

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
key = os.getenv("KEY")
secret = os.getenv("SECRET")


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)

api = tweepy.API(auth)

hashtag = "#fed"
tweetNumber = 2

tweets = tweepy.Cursor(api.search, hashtag).items(tweetNumber)

def searchBot():
    for tweet in tweets:
        try:
            tweet.retweet()
            print("Retweet done!")
            time.sleep(2)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)
searchBot()
