import tweepy
from textblob import TextBlob
import alpaca_trade_api as tradeapi
import csv
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
client = redis.Redis(host="10.10.10.1", port=6379, db=0,
                     password=os.getenv("REDIS_PASS"))
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
auth.secure = True
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
png_file = "/tmp/plot.png"

APCA_API_BASE_URL = os.getenv("APCA_API_BASE_URL")
APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
alpaca = tradeapi.REST(APCA_API_KEY_ID,
                    APCA_API_SECRET_KEY,
                    APCA_API_BASE_URL,
                    api_version='v2'
                    )
correct = 0
wrong = 0


def get_all_tweets(screen_name):
    #Twitter only allows access to a users most recent 3240 tweets with this method

    #initialize a list to hold all the tweepy Tweets
    alltweets = []

    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=200)

    #save most recent tweets
    alltweets.extend(new_tweets)

    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print(f"getting tweets before {oldest}")

        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(
            screen_name=screen_name, count=200, max_id=oldest)

        #save most recent tweets
        alltweets.extend(new_tweets)

        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print(f"...{len(alltweets)} tweets downloaded so far")

    #transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [[tweet.id_str, tweet.created_at, tweet.text]
                 for tweet in alltweets]

    #write the csv
    with open(f'new_{screen_name}_tweets.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "created_at", "text"])
        writer.writerows(outtweets)

    pass

def readTweets():
    reader = csv.DictReader(open("new_interntendie_tweets.csv"))
    for raw in reader:
        if "bullish" in raw["text"]:
            client.sadd("bullish_date", str(raw["created_at"][:-9]))
        elif "bearish" in raw["text"]:
            client.sadd("bearish_date", str(raw["created_at"][:-9]))
    print(client.scard("bullish_date"))
    print(client.scard("bearish_date"))

def preferBullish():
    bullish = client.smembers("bullish_date")
    bearish = client.smembers("bearish_date")
    delete = 0
    for date in bullish:
        if date in bearish:
            print(date.decode("utf-8"))
            client.srem("bearish_date", date.decode("utf-8"))
            delete += 1
    print(f"removed {delete} dates from bearish")

def checkAccuracy():
    bullishDates = client.smembers("bullish_date")
    bearishDates = client.smembers("bearish_date")
    for date in bullishDates:
        date = date.decode("utf-8") + "T09:30:00-04:00"
        ifBullish(date)

    for date in bearishDates:
        date = date.decode("utf-8") + "T09:30:00-04:00"
        ifBearish(date)
    getPct()
    

def ifBullish(date):
    global correct
    global wrong
    bars = alpaca.get_barset("SPY", "day", start=date, limit=100)
    day1 = bars["SPY"][0].c
    try:
        day2 = bars["SPY"][1].c
    except Exception as e:
        print(e)
        return
    
    if day2 > day1:
        correct += 1
    else:
        wrong += 1


def ifBearish(date):
    global correct
    global wrong
    bars = alpaca.get_barset("SPY", "day", start=date, limit=100)
    day1 = bars["SPY"][0].c
    try:
        day2 = bars["SPY"][1].c
    except Exception as e:
        print(e)
        return
    if day2 > day1:
        wrong += 1
    else:
        correct += 1


def getPct():
    pct = (correct / (correct + wrong)) * 100
    print(f"Correct: {correct} Incorrect: {wrong}")
    print(f"Percentage of accuracy: {pct}%")


def main():
    #pass in the username of the account you want to download
	# get_all_tweets("interntendie")
    # readTweets()
    # preferBullish()
    # checkAccuracy()
    print(client.scard("bullish_date"))
    print(client.scard("bearish_date"))
    # acct = api.get_user("interntendie")
    # print(acct.followers_count)

if __name__ == "__main__":
    main()
