# Twitter Bot Implementing Redis Database 

This is messing around learning python using tweepy and twitter API to automate twitter functions. Some functions used in this are 
tweeting, replying to mentions, following users back and more. Most of the examples I've seen online were reading and writing from files, however, in my opinion redis is as easy, if not easier, to use.

## Prerequisites
**Twitter Developer Set Up**
* Sign into Twitter at apps.twitter.com
* Create a new application and fill out your information
* Generate your access token
* Write down your needed keys
  * Consumer ID
  * Consumer Secret Key
  * Key ID
  * Secret Key ID

**Redis Setup**
* Download redis and activate your redis server a simple youtube search will do
* Start running your redis-server
* Next open your redis-cli
  * Be sure to change the requirepass within your config to secure your server
  * Within redis-cli// > config get requirepass
    1. "requirepass"
    2. "This Will Be Empty"
* Set your password
  * Within redis-cli// > config set requirepass yourPasswordHere (recommended at least 32 characters long)



## Running

This is built to be ran 24/7 using docker.

```bash
docker run -d \
  --name bot_name \
  --restart unless-stopped \
  -e CONSUMER_KEY="some consumer ID" \
  -e CONSUMER_SECRET="some consumer secret KEY" \
  -e KEY="some key ID" \
  -e SECRET="some secret key ID" \
  -e REDIS_PASS="some password" \
  10.10.10.1:5000/bot-name
```
