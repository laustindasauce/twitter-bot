import csv
import datetime
import numpy as np
import os
import re
import redis
import schedule
from textblob import TextBlob
import time
import tweepy

### Twitter
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
key = os.getenv("KEY")
secret = os.getenv("SECRET")

### Redis

client = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, db= 1, password=os.getenv("REDIS_PASS"))

### Tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
auth.secure = True
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

### Global Variables
correct = 0
wrong = 0

if client.get('last_seen_id') is None:
    client.set('last_seen_id', '1194877411671724066')
    client.set('read', '53309254')
    client.set('sent_number', '379')
    client.set('highest_sentiment', '309')
    client.set('lowest_sentiment', '-334')

if client.get('twit_bot') is None:
    client.set('twit_bot', 'bullish')

def read_last_seen():
    last_seen_id = int(client.get('last_seen_id'))
    return last_seen_id


def store_last_seen(last_seen_id):
    client.set('last_seen_id', str(last_seen_id))
    return


def reply():
    tweets = api.mentions_timeline(read_last_seen(), tweet_mode='extended')
    for tweet in reversed(tweets):
        client.incr("tendie_read")
        try:
            username = tweet.user.screen_name
            
            print("Favorited " + username +
                    " - " + tweet.full_text)
            api.create_favorite(tweet.id)
            store_last_seen(tweet.id)
        except tweepy.TweepError as e:
            store_last_seen(tweet.id)
            print(e.reason)
        time.sleep(2)

def specific_favorite():
    '''
    Could use something like this to get trending tickers
    Just follow thousands of people who tweet regularly about the stock market
    Each time you find a tweet with stock market in it or a ticker in it follow that person
    '''
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


def tweet_sentiment():
    print("Running tweet_sentiment()")
    client = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, password=os.getenv("REDIS_PASS"))
    sentiment = client.get('twit_bot').decode("utf-8")
    status = f"I am currently {sentiment} the stock market."
    print(status)
    api.update_status(status)
    client.set("tendie_recent", status)


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
                client.sadd(redisDataBase, (str(tweet.full_text.replace('\n', '').encode("utf-8"))+"\n"))
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

    bullish_count -= 35
    sentiment = (bullish_count) - bearish_count
    client.incr('sent_number')
    sent_num = int(client.get('sent_number'))
    to_string = f"Reading #{sent_num} => Twitter's sentiment of the stock market is"
    weekday = datetime.datetime.today().weekday() < 5
    if sentiment > 5:
        client.sadd("bullish_date", str(datetime.date.today()))
        to_string = f"{to_string} bullish with a reading of {sentiment}."
        current_high = int(client.get('highest_sentiment'))
        if sentiment > current_high:
            client.set('highest_sentiment', str(sentiment))
            to_string = f"{to_string} This is the highest reading to date."
        if weekday: 
            client.incr('weekly_bulls')
    elif sentiment > -5:
        to_string = f"{to_string} nuetral with a reading of {sentiment}."
        if weekday: 
            client.incr('weekly_nuetral')
    else:
        client.sadd("bearish_date", str(datetime.date.today()))
        to_string = f"{to_string} bearish with a reading of {sentiment}."
        current_low = int(client.get('lowest_sentiment'))
        if sentiment < current_low:
            client.set('lowest_sentiment', str(sentiment))
            to_string = f"{to_string} This is the lowest reading to date."
        if weekday: 
            client.incr('weekly_bears')
    print(to_string)
    today = datetime.datetime.now()
    today = ":".join(str(today).split(":")[0:2])
    storage_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, db= 4, password=os.getenv("REDIS_PASS"))
    res = storage_client.hset('total_tendie_readings', today, str(sentiment))
    if res != 1:
        print(f"Error adding new reading to storage client: {today} {sentiment}")
    api.update_status(to_string)


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

def weekly_sentiment():
    if client.get('weekly_bulls') is None and client.get('weekly_bears') is None and client.get('weekly_nuetral') is None:
        print("Weekly stats weren't set")
        clear_weekly()
        return
    bulls = int(client.get('weekly_bulls'))
    bears = int(client.get('weekly_bears'))
    split = int(client.get('weekly_nuetral'))
    total = bulls + bears + split
    week_sentiment = ''
    if bulls > bears:
        week_sentiment = 'bullish'
    elif bears > bulls:
        week_sentiment = 'bearish'
    else:
        week_sentiment = 'nuetral'
    today = datetime.date.today()
    last_monday = str(today - datetime.timedelta(days=today.weekday()))
    today = str(today)
    adjTimeframe = f" {last_monday[-5:]} - {today[-5:]}"
    
    
    to_string = f"From {adjTimeframe} at close there were {total} stock market sentiment readings." + \
    f" Sentiment was {week_sentiment} with {bulls} bullish, {bears} bearish, and {split} nuetral readings."

    client.hset('stock_sentiment', today, week_sentiment)

    api.update_status(to_string)
    clear_weekly()

def clear_weekly():
    client.set('weekly_bulls', '0')
    client.set('weekly_bears', '0')
    client.set('weekly_nuetral', '0')
    

def thank_new_followers():
    total_followers = client.scard('followers_thanked')
    followers_thanked = []
    followers = []
    for follower in list(client.smembers('followers_thanked')):
        followers_thanked.append(follower.decode("utf-8"))
    followers_thanked = set(followers_thanked)
    follow_count = 0
    limit = False
    for follower in tweepy.Cursor(api.followers).items(10):
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
        for follower in new_followers:
            client.sadd('followers_thanked', str(follower))
        trouble = False
        to_string = "\nAppreciate you following me! I am a fully automated twitter account. If you're interested in programming or if you'd like to create an automated twitter account of your own, I can send you a link to my GitHub Repository!\n" + \
            "If your next message has 'yes' anywhere in it I will send you a link!"
        if limit:
            to_string = f"{to_string}\nSorry, I've hit a following limit and will follow you back ASAP!"
        for follower in new_followers:
            if not trouble:
                try:
                    client.sadd('followers_thanked', str(follower))
                    # api.send_direct_message(follower, to_string)
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
    time.sleep(60)


def send_error_message(follower):
    try:
        to_string = "I errored out.. going to sleep for 2 hours.."
        api.send_direct_message(follower, to_string)
        print("Sent dm to 441228378 since we errored out.")
    except tweepy.TweepError as e:
        if e.reason[:13] != "[{'code': 139" or e.reason[:13] != "[{'code': 226" or e.reason[:13] != "[{'code': 429":
            print(e.reason)
        time.sleep(10*60)
        send_error_message(441228378)


# def get_all_tweets(screen_name):
#     #Twitter only allows access to a users most recent 3240 tweets with this method

#     #initialize a list to hold all the tweepy Tweets
#     alltweets = []

#     #make initial request for most recent tweets (200 is the maximum allowed count)
#     new_tweets = api.user_timeline(screen_name=screen_name, count=200)

#     #save most recent tweets
#     alltweets.extend(new_tweets)

#     #save the id of the oldest tweet less one
#     oldest = alltweets[-1].id - 1

#     #keep grabbing tweets until there are no tweets left to grab
#     while len(new_tweets) > 0:
#         print(f"getting tweets before {oldest}")

#         #all subsiquent requests use the max_id param to prevent duplicates
#         new_tweets = api.user_timeline(
#             screen_name=screen_name, count=200, max_id=oldest)

#         #save most recent tweets
#         alltweets.extend(new_tweets)

#         #update the id of the oldest tweet less one
#         oldest = alltweets[-1].id - 1

#         print(f"...{len(alltweets)} tweets downloaded so far")

#     #transform the tweepy tweets into a 2D array that will populate the csv
#     outtweets = [[tweet.id_str, tweet.created_at, tweet.text]
#                  for tweet in alltweets if tweet.text[:7] == "Reading" or tweet.text[:7] == "Twitter"]

#     #write the csv
#     with open(f'new_{screen_name}_tweets.csv', 'w') as f:
#         writer = csv.writer(f)
#         writer.writerow(["id", "created_at", "text"])
#         writer.writerows(outtweets)

#     pass

def readTweets():
    client = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, db= 4, password=os.getenv("REDIS_PASS"))
    reader = csv.DictReader(open("tweets.csv"))
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
            res = client.hset('total_tendie_readings', reading_time, reading_val)
            if res != 1:
                print("Error setting this value as hash in redis")
                print(reading_time, reading_val)
        

    print(f'{total_readings} stock market sentiment readings stored in Redis')


# get_all_tweets("InternTendie")
# readTweets()

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

###### Schedule Weekly Sentiment Job ########
schedule.every().friday.at("17:00").do(weekly_sentiment)


print("Running twitter-bot")
# run_scraper()


while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except tweepy.TweepError as e:
        print(e.reason)
        send_error_message(441228378)
        time.sleep(2*60*60)


# Author -- Austin Spencer