import datetime
import tweepy
from textblob import TextBlob
# import alpaca_trade_api as tradeapi
import csv
# import pandas as pd
# import matplotlib.pyplot as plt
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
# client = redis.Redis(host="10.10.10.1", port=6379, db=0,
#                      password=os.getenv("REDIS_PASS"))
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
auth.secure = True
api = tweepy.API(auth)
png_file = "/tmp/plot.png"


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
                 for tweet in alltweets if tweet.text[:7] == "Reading" or tweet.text[:7] == "Twitter"]

    #write the csv
    with open(f'new_{screen_name}_tweets.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "created_at", "text"])
        writer.writerows(outtweets)

    pass

def readTweets():
    # client = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, db= 4, password=os.getenv("REDIS_PASS"))
    reader = csv.DictReader(open("new_interntendie_tweets.csv"))
    total_readings = 0

    for line in reader:
        reading_val = None
        
        text = line["text"].replace('.', '')
        reading_time = ":".join(line["created_at"].split(":")[0:2])

        text_list = text.split()
        for word in text_list:
            if word.isnumeric():
                reading_val = word
                total_readings += 1

        if not reading_val:
            # Negative number
            text = text.replace('-', '')
            text_list = text.split()
            for word in text_list:
                if word.isnumeric():
                    reading_val = f'-{word}'
                    total_readings += 1
        if reading_val:
            print(f'total_tendie_readings {reading_time} {reading_val}')
            # res = client.hset('total_tendie_readings', reading_time, reading_val)
            # if res != 1:
            #     print("Error setting this value as hash in redis")
            #     print(reading_time, reading_val)


def main():
    # addDataList()
    #pass in the username of the account you want to download
	# get_all_tweets("InternTendie")
    readTweets()
    today = datetime.datetime.now()
    today = ":".join(str(today).split(":")[0:2])
    print(today)
    # preferBullish()
    # checkAccuracy()
    # print(client.get("tendie_pct"))
    # client.set("testing", str(datetime.date.today()))
    # print(client.get("testing"))
    # print(client.scard("bullish_date"))
    # print(client.scard("bearish_date"))
    # acct = api.get_user("interntendie")
    # print(acct.followers_count)

if __name__ == "__main__":
    main()