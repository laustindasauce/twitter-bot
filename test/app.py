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
client = redis.Redis(host="10.10.10.1", port=6379, db=0,
                     password=os.getenv("REDIS_PASS"))
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
auth.secure = True
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
png_file = "/tmp/plot.png"


def main():
    acct = api.get_user("interntendie")
    print(acct.status._json["text"])

if __name__ == "__main__":
    main()