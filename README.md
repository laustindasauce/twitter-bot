# Twitter Bot 

This is some code using tweepy and twitter API to automate some twitter functions.

## Prerequisites
**Twitter Developer Set Up**
* Sign into Twitter at apps.twitter.com
* Create a new application and fill out your information
* Generate your access token
* Write down your needed keys
 - Consumer ID
 - Consumer Secret Key
 - Key ID
 - Secret Key ID

**Redis Setup**
* Download redis and activate your redis server a simple youtube search will do
* Start running your redis-server
* Next open your redis-cli
 - Be sure to change the requirepass within your config to secure your server
 - Within redis-cli// > config get requirepass
 - 1) "requirepass"
 - 2) "This Will Be Empty"
* Set your password
 - Within redis-cli// > config set requirepass yourPasswordHere


### Running

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