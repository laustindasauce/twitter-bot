import datetime
import os
import re
import redis
import schedule
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
                client.sadd(redisDataBase, (str(tweet.full_text.replace(
                    '\n', '').encode("utf-8"))+"\n"))
            tweetCount += len(new_tweets)
            max_id = new_tweets[-1].id
            download = (tweetCount / maxTweets) * 100
            print(f"Downloading tweets -> {download}%")
        except tweepy.TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
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
    if sentiment > 5:
        client.sadd("bullish_date", str(datetime.date.today()))
        to_string = f"{to_string} bullish with a reading of {sentiment}."
        current_high = int(client.get('highest_sentiment'))
        if sentiment > current_high:
            client.set('highest_sentiment', str(sentiment))
            to_string = f"{to_string} This is the highest reading to date."
    elif sentiment > -5:
        to_string = f"{to_string} nuetral with a reading of {sentiment}."
    else:
        client.sadd("bearish_date", str(datetime.date.today()))
        to_string = f"{to_string} bearish with a reading of {sentiment}."
        current_low = int(client.get('lowest_sentiment'))
        if sentiment < current_low:
            client.set('lowest_sentiment', str(sentiment))
            to_string = f"{to_string} This is the lowest reading to date."
    print(to_string)
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


####### Set Our Scheduled Jobs ########
schedule.every(15).minutes.do(thank_new_followers)
schedule.every(7).hours.do(run_scraper)
schedule.every().day.at("15:13").do(tweet_sentiment)
schedule.every().thursday.at("03:37").do(unfollow)
schedule.every().week.do(unfollow)

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