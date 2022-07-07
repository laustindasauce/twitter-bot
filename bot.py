import csv
import datetime
import numpy as np
import os
import psycopg2
import pytz
import re
import schedule
from textblob import TextBlob
import time
import tweepy

### Twitter
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
key = os.getenv("KEY")
secret = os.getenv("SECRET")
ID = "1243690297747312642"

### PSQL
host = os.getenv("POSTGRESQL_HOST") or "localhost"
db = os.getenv("POSTGRESQL_DB") or "personal_db"
user = os.getenv("POSTGRESQL_USER") or "gaming_admin"
password = os.getenv("POSTGRESQL_PASSWORD") or "secret_password"
port = os.getenv("POSTGRESQL_PORT") or "5432"

### Tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
auth.secure = True
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

### Global Variables
correct = 0
wrong = 0
timezone = pytz.timezone("America/Los_Angeles")


def add_sentiment_reading(
    sentiment: int, date: datetime = timezone.localize(datetime.datetime.now())
):
    try:
        conn = psycopg2.connect(
            host=host, database=db, user=user, password=password, port=port
        )
        cursor = conn.cursor()
        # Update single record now
        sql = """INSERT INTO twitter_sentiment (account_id, date, value) VALUES (%s, %s , %s)"""
        cursor.execute(sql, (ID, date, sentiment))
        conn.commit()
        count = cursor.rowcount
        print(count, "Record added successfully ")
    except Exception as e:
        print(e)


def update_tweets_read(amount: int):
    try:
        conn = psycopg2.connect(
            host=host, database=db, user=user, password=password, port=port
        )
        cursor = conn.cursor()
        # Update single record now
        sql_update_query = (
            """Update twitter_account set tweets_read = %s where id = %s"""
        )
        cursor.execute(sql_update_query, (amount, ID))
        conn.commit()
        count = cursor.rowcount
        print(count, "Record Updated successfully ")
    except Exception as e:
        print(e)


def get_sentiment_reading_count():
    try:
        conn = psycopg2.connect(
            host=host, database=db, user=user, password=password, port=port
        )
        cursor = conn.cursor()
        # query to count total number of rows
        sql = f"SELECT count(*) from twitter_sentiment where account_id = '{ID}';"
        data = []

        # execute the query
        cursor.execute(sql, data)
        results = cursor.fetchone()

        # loop to print all the fetched details
        for r in results:
            print(r)
        print("Total number of rows in the table:", r)
        return r
    except Exception as e:
        print(e)


def get_sentiment_extremes(extreme: str = "max"):
    try:
        conn = psycopg2.connect(
            host=host, database=db, user=user, password=password, port=port
        )
        cursor = conn.cursor()
        # query to get the max or min value from twitter sentiment
        sql = (
            f"SELECT {extreme}(value) from twitter_sentiment where account_id = '{ID}';"
        )
        data = []

        # execute the query
        cursor.execute(sql, data)
        results = cursor.fetchone()

        # loop to print all the fetched details
        for r in results:
            print(r)
        print(f"{extreme} of twitter sentiment readings: ", r)
        return r
    except Exception as e:
        print(e)


def get_account_followers(extreme: str = "max"):
    try:
        conn = psycopg2.connect(
            host=host, database=db, user=user, password=password, port=port
        )
        cursor = conn.cursor()
        # query to get the max or min value from twitter sentiment
        sql = (
            f"SELECT {extreme}(value) from twitter_sentiment where account_id = '{ID}';"
        )
        data = []

        # execute the query
        cursor.execute(sql, data)
        results = cursor.fetchone()

        # loop to print all the fetched details
        for r in results:
            print(r)
        print(f"{extreme} of twitter sentiment readings: ", r)
        return r
    except Exception as e:
        print(e)


def scrape_twitter(maxTweets, searchQuery, file_name):
    print(f"Downloading max {maxTweets} tweets")
    retweet_filter = "-filter:retweets"
    q = searchQuery + retweet_filter
    tweetCount = 0
    max_id = -1
    tweetsPerQry = 100
    sinceId = None
    with open(file_name, "w") as file:
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
                    tweet = str(tweet.full_text.replace("\n", "")) + "\n"
                    file.write(tweet)
                tweetCount += len(new_tweets)
                max_id = new_tweets[-1].id
                download = (tweetCount / maxTweets) * 100
                print(f"Downloading tweets -> {download}%")
            except tweepy.TweepError as e:
                # Just exit if any error
                print("Some error : " + str(e))
                break
    print(f"Downloading tweets -> 100%")


def clean(tweet):
    tweet = re.sub(r"^RT[\s]+", "", tweet)
    tweet = re.sub(r"https?:\/\/.*[\r\n]*", "", tweet)
    tweet = re.sub(r"#", "", tweet)
    tweet = re.sub(r"@[A-Za-z0–9]+", "", tweet)
    return tweet


def read_tweets(file_name):
    tweets = []
    with open(file_name, "r") as file:
        f = file.readlines()
        tweets = [clean(sentence.strip()) for sentence in f]

    return tweets


def polarity(x):
    return TextBlob(x).sentiment.polarity


def subjectivity(x):
    return TextBlob(x).sentiment.subjectivity


def run_scraper():
    print("Running data scraper.")
    file_name = "scraper_data.txt"
    scrape_twitter(100, "stock market", file_name)
    f = read_tweets(file_name)
    tweet_polarity = np.zeros(len(f))
    tweet_subjectivity = np.zeros(len(f))
    bullish_count = 0
    bearish_count = 0

    for idx, tweet in enumerate(f):
        tweet_polarity[idx] = polarity(tweet)
        tweet_subjectivity[idx] = subjectivity(tweet)
        if tweet_polarity[idx] > 0.15 and tweet_subjectivity[idx] < 0.5:
            bullish_count += 1
        elif tweet_polarity[idx] < 0.00 and tweet_subjectivity[idx] < 0.5:
            bearish_count += 1

    bullish_count -= 35
    sentiment = (bullish_count) - bearish_count
    sent_num = get_sentiment_reading_count() + 1
    to_string = f"Reading #{sent_num} => Twitter's sentiment of the stock market is"
    if sentiment > 5:
        to_string = f"{to_string} bullish with a reading of {sentiment}."
        current_high = get_sentiment_extremes("max")
        if sentiment > current_high:
            to_string = f"{to_string} This is the highest reading to date."
    elif sentiment > -5:
        to_string = f"{to_string} nuetral with a reading of {sentiment}."
    else:
        to_string = f"{to_string} bearish with a reading of {sentiment}."
        current_low = get_sentiment_extremes("min")
        if sentiment < current_low:
            to_string = f"{to_string} This is the lowest reading to date."
    print(to_string)
    add_sentiment_reading(sentiment=sentiment)
    # api.update_status(to_string)
    os.remove(file_name)


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
    try:
        new = 0
        for follower in tweepy.Cursor(api.get_followers).items(20):
            # follower has a long list of possible things to see.. kinda neat
            if not follower.following:
                try:
                    follower.follow()
                    time.sleep(3)
                    new += 1
                    # Moved this print statement so that if there is an error we don't print
                except tweepy.TweepyException as e:
                    """Ignores error that we've already tried to follow this person
                    The reason we're ignoring this error is because if someone is private
                    we will keep trying to follow them until they accept our follow.
                    """
                    if "160" in str(e):
                        return
                    time.sleep(2)
        if new > 0:
            print(f"Followed {new} people.")
    except tweepy.TweepyException as e:
        error_message = f"Exception in thank_new_followers: {str(e)}"
        raise Exception(error_message)


def send_error_message(follower):
    try:
        to_string = "I errored out.. going to sleep for 2 hours.."
        api.send_direct_message(follower, to_string)
        print("Sent dm to 441228378 since we errored out.")
    except tweepy.TweepError as e:
        if (
            e.reason[:13] != "[{'code': 139"
            or e.reason[:13] != "[{'code': 226"
            or e.reason[:13] != "[{'code': 429"
        ):
            print(e.reason)
        time.sleep(10 * 60)
        send_error_message(441228378)


def get_all_tweets(screen_name):
    print("Getting tweets")
    # Twitter only allows access to a users most recent 3240 tweets with this method

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=200)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print(f"getting tweets before {oldest}")

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(
            screen_name=screen_name, count=200, max_id=oldest
        )

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print(f"...{len(alltweets)} tweets downloaded so far")

    # transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [
        [tweet.id_str, tweet.created_at, tweet.text]
        for tweet in alltweets
        if tweet.text[:7] == "Reading" or tweet.text[:7] == "Twitter"
    ]

    # write the csv
    with open(f"new_{screen_name}_tweets.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "created_at", "text"])
        writer.writerows(outtweets)

    pass


def readTweets(screen_name):
    reader = csv.DictReader(open(f"new_{screen_name}_tweets.csv"))
    total_readings = 0

    for line in reader:
        reading_val = None

        text = line["text"].replace(".", "")
        reading_time = ":".join(line["created_at"].split(":")[0:2])

        text_list = text.split()
        for word in text_list:
            if word.isnumeric():
                reading_val = word
                total_readings += 1

        if not reading_val:
            # Negative number
            text = text.replace("-", "")
            text_list = text.split()
            for word in text_list:
                if word.isnumeric():
                    reading_val = f"-{word}"
                    total_readings += 1
        if reading_val:
            add_sentiment_reading(
                sentiment=int(reading_val),
                date=datetime.datetime.fromisoformat(reading_time),
            )

    print(f"{total_readings} stock market sentiment readings stored in psql db")


####### Schedule Twitter Jobs ########
schedule.every(15).minutes.do(thank_new_followers)
# schedule.every().day.at("15:13").do(tweet_sentiment)
schedule.every().thursday.at("03:37").do(unfollow)
schedule.every().week.do(unfollow)

####### Schedule Scraper Jobs ########
schedule.every().day.at("08:30").do(run_scraper)
schedule.every().day.at("12:00").do(run_scraper)
schedule.every().day.at("15:00").do(run_scraper)
schedule.every().day.at("22:00").do(run_scraper)

# print("Running twitter-bot")
# run_scraper()
# get_all_tweets("InternTendie")
# readTweets("InternTendie")
# update_tweets_read(amount=53325800)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except tweepy.TweepError as e:
        print(e.reason)
        send_error_message(441228378)
        time.sleep(2 * 60 * 60)


# Author -- Austin Spencer
