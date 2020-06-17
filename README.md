# Twitter Bot 

This is some code using tweepy and twitter API to automate some twitter functions.

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