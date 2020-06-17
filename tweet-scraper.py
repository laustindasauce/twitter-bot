import tweepy
from textblob import TextBlob
import jsonpickle
import pandas as pd
import numpy as np
import redis
import re
import os
import json
import seaborn as sns
import matplotlib.pyplot as plt

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
    while tweetCount < maxTweets:
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
            print(f"Downloaded {tweetCount} tweets")
            max_id = new_tweets[-1].id

        except tweepy.TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break

    print(f"Downloaded {tweetCount} tweets, Saved to {redisDataBase}")

    # print(client.smembers(redisDataBase))


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


if __name__ == "__main__":
    redisDataBase = "tweets_scraped"
    scrape_twitter(1000, 'trump', redisDataBase)
    f = read_tweets(redisDataBase)
    # print(f)
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
    #                 s=100)
    sentiment = bullish_count - bearish_count
    print(f"Bullish count is {bullish_count}")
    print(f"Bearish count is {bearish_count}")
    if sentiment > 30:
        print("The market sentiment is bullish!!")
    elif sentiment > 0:
        print("Twitter sentiment is showing people undecided on whether the market is currently bullish or bearish.")
    else:
        print("The market is bearish")
    print(sentiment)

    # plt.title("Sentiment Analysis", fontsize=20)
    # plt.xlabel('← Negative — — — — — — Positive →', fontsize=15)
    # plt.ylabel('← Facts — — — — — — — Opinions →', fontsize=15)
    # plt.tight_layout()
    # plt.show()

