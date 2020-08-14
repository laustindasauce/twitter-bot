# Twitter Bot Implementing Redis Database 
This learning python using tweepy and twitter API to automate twitter functions. Some functions used in this are automatically tweeting, replying to mentions, following users back and more. Most of the examples I've seen online were reading and writing from files, however, in my opinion redis is as easy, if not easier, to use. It also lowers CPU storage space, especially while doing the sentiment analysis which can download thousands of tweets.

## Prerequisites

### Twitter Developer Set Up
* Sign into Twitter [here](apps.twitter.com)
* Create a new application and fill out your information
* Generate your access token
* Write down your needed keys
  * Consumer ID
  * Consumer Secret Key
  * Key ID
  * Secret Key ID

### Redis Setup
* Download redis and activate your redis server -> [youtube example](https://www.youtube.com/watch?v=dlI-xpQxcuE)
* Start running your redis-server
* Next open your redis-cli
  * Be sure to change the requirepass within your config to secure your server
  * Within redis-cli// > config get requirepass
    1. "requirepass"
    2. "This Will Be Empty"
* Set your password
  * Within redis-cli// > config set requirepass yourPasswordHere (recommended at least 32 characters long)



## Running

### This is built to be ran 24/7 using docker

```bash
docker pull 10.10.10.1:5000/bot-name \
&& docker run -d \
  --name bot_name \
  --restart unless-stopped \
  -e CONSUMER_KEY="some consumer ID" \
  -e CONSUMER_SECRET="some consumer secret KEY" \
  -e KEY="some key ID" \
  -e SECRET="some secret key ID" \
  -e REDIS_PASS="some password" \
  10.10.10.1:5000/bot-name
```

## Build & Push 

### Docker Container
**Make sure you are in the directory that has you Dockerfile and bot script**
```bash
docker build --no-cache -t 10.10.10.1:5000/bot-name .

docker push 10.10.10.1:5000/bot-name
```

## Contributions are welcomed! 💚
**If you have any ideas, talk to me here: [![Issues][1.4]][1]**

**Check out my personal bot account here: [![Twitter][1.2]][2]**



<!-- link to issues page -->

[1]: https://github.com/abspen1/twitter-bot/issues

<!-- links to your social media accounts -->

[2]: https://twitter.com/interntendie

<!-- icons without padding -->

[1.2]: http://i.imgur.com/wWzX9uB.png (twitter icon without padding)
[1.4]: https://i.imgur.com/2SqWbO1.png (mail icon without padding)