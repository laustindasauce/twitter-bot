# Running Locally

## Redis Setup
* Download redis and activate your redis server -> [youtube example](https://www.youtube.com/watch?v=dlI-xpQxcuE)
* Start running your redis-server
* Next open your redis-cli
  * Be sure to change the requirepass within your config to secure your server
  * Within redis-cli// > config get requirepass
    1. "requirepass"
    2. "This Will Be Empty"
* Set your password
  * Within redis-cli// > config set requirepass yourPasswordHere (recommended >= 32 characters)

## Docker Setup (if you don't want to use Docker skip to [here](#running-locally-without-docker))
* Mac [instructions](https://www.robinwieruch.de/docker-macos)
* Windows [instructions](https://docs.docker.com/docker-for-windows/install/)


## Build and Run Docker Images
Build your image and then run the image as a Docker container with the commands below.
* FIRST cd into your working directory with Dockerfile and bot.py
```bash
$ docker build twitter-bot

$ docker run -d \
  --name bot_name \
  --restart unless-stopped \
  -e CONSUMER_KEY="some consumer ID" \
  -e CONSUMER_SECRET="some consumer secret KEY" \
  -e KEY="some key ID" \
  -e SECRET="some secret key ID" \
  -e REDIS_PASS="some password" \
  -v $PWD:/work \
  twitter-bot
```

**Pull from previous build (optional)**
```bash
docker pull bot-name \
&& docker run -d \
  --name bot_name \
  --restart unless-stopped \
  -e CONSUMER_KEY="some consumer ID" \
  -e CONSUMER_SECRET="some consumer secret KEY" \
  -e KEY="some key ID" \
  -e SECRET="some secret key ID" \
  -e REDIS_PASS="some password" \
  bot-name
```

### Build & Push to remote portainer

**Make sure you are in the directory that has your Dockerfile and bot script**
```bash
docker build --no-cache -t 10.0.0.1:PORT/bot-name .

docker push 10.0.0.1:PORT/bot-name
```

## Running locally without Docker

### Dependencies
You will need to pip install the following packages if you want to run this bot locally without Docker.

* Using requirements.txt
```bash
pip install -r requirements.txt
```

* pip install manually
```bash
pip install redis
pip install schedule
pip install tweepy

# If you don't plan on using sentiment analysis ignore these
pip install matplotlib
pip install numpy
pip install pandas
pip install seaborn
pip install textblob
```

### Setup local Environment
* Be sure to cd into your working directory that contains your bot.py script
* Export your variables so you can access them with os.getenv() (Mac OS)
```bash
export CONSUMER_KEY="your key" \
&& export CONSUMER_SECRET="your secret" \
&& export SECRET="your secret"\
&& export HOST="external ip address" \
&& export REDIS_PASS="your redis password"\
&& export KEY="your key"
```
* Now you are ready to run your script
```bash
python bot.py
```