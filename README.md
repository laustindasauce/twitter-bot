# Twitter Bot [![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fabspen1%2Ftwitter-bot&count_bg=%2300ACEE&title_bg=%23555555&icon=twitter.svg&icon_color=%2300ACEE&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
Learning python using tweepy and twitter API to automate twitter functions. Some functions used in this are automatically tweeting, replying to mentions, following users back and more. Most of the examples I've seen online were reading and writing from files, however, in my opinion Redis database is as easy, if not easier, to use. Redis also lowers CPU storage space, especially while doing the sentiment analysis which can download thousands of tweets. For more reliable 24/7 running, I built this script into a Docker container. Checkout the [webpage](https://abspen1.github.io/twitter-bot/) for some statistics of my account!

# Prerequisites

### Twitter Developer Set Up
* Sign into Twitter [here](https://developer.twitter.com/en/docs/twitter-api/getting-started/guide)
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


# Running
**Be sure to CD into your working directory with dockerfile and bot.py within**

### Be sure to export your variables to be read with os.getenv()
```bash
export CONSUMER_KEY="your key" \
&& export CONSUMER_SECRET="your secret" \
&& export SECRET="your secret"\
&& export REDIS_PASS="your redis password"\
&& export KEY="your key"
```

# Running 24/7 with Docker in Google Cloud Instance
* First you need to set up your Google Cloud Instance
 * I suggest youtube to help you set it up
 * You will need to go to [Google Cloud Platform](https://cloud.google.com/gcp/?utm_source=google&utm_medium=cpc&utm_campaign=na-US-all-en-dr-skws-all-all-trial-b-dr-1009135&utm_content=text-ad-none-any-DEV_c-CRE_109860918967-ADGP_Hybrid+%7C+AW+SEM+%7C+SKWS+%7C+US+%7C+en+%7C+Multi+~+Cloud-KWID_43700009609890930-kwd-19383198255&utm_term=KW_%2Bcloud-ST_%2Bcloud&&gclid=Cj0KCQjwv7L6BRDxARIsAGj-34qcziciZyZZMes6maVVBfg7lmWjgqQkUNXdwg8lHqQwTPVtNEWX0xoaAgGPEALw_wcB)
 * Then to console where you can set up your compute engine
 * Watch this video for help with inital setup [video](https://www.youtube.com/watch?v=p5wl1s5gKY0)
### ssh into your vm instance
* I prefer to do this on my local machine but you can also do it in browser within a shell
* Install gcloud sdk on your local machine.. steps are [here](https://cloud.google.com/sdk/docs/downloads-interactive)
 * There will be a generated ssh that you can copy and paste into your terminal to ssh into your vm instance using gcloud
![Alt text](/images/ssh.png "ssh")
* Once you're inside your instance within your terminal it should look something like this
![Alt text](/images/terminal.png "instance")
### Download Docker
* Awesome instructions [here](http://docs.h2o.ai/driverless-ai/latest-stable/docs/userguide/install/google-docker-container.html)
* Note that you will likely need to add sudo infront of each command
```bash
# SCRIPT FOR CPUs ONLY
apt-get -y update

# If you have issues with this command, omit the python-software-properties
apt-get -y --no-install-recommends install \
  curl \
  apt-utils \
  python-software-properties \
  software-properties-common

add-apt-repository -y "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# If you need to add sudo as prefix to these commands be sure to add sudo in front of the "apt-key add -"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

apt-get update
apt-get install -y docker-ce
```
Check that install worked
* $ docker --version 
* If this shows your docker version then you've successfully installed docker on your vm instance
### clone your git repository to run within docker
* First check that git is installed
* $ git --version
* $ git clone https://github.com/abspen1/twitter-bot.git
* $ ls (check that the repo cloned into your instance)

### Build the docker image
* cd into twitter-bot directory
* $ sudo docker build -t bot .

### Check if image was created
$ sudo docker image ls

### Run docker image in a container
```bash
$ sudo docker run -d \
  --name bot_name \
  --restart unless-stopped \
  -e CONSUMER_KEY="some consumer ID" \
  -e CONSUMER_SECRET="some consumer secret KEY" \
  -e KEY="some key ID" \
  -e SECRET="some secret key ID" \
  -e REDIS_PASS="some password" \
  -v $PWD:/work \
  bot
```

### Check that the container is running
* $ sudo docker container ls
* $ sudo docker logs bot_name


## Google Cloud Terminal Commands
![Alt text](/images/cmds1.png "cmds1")
![Alt text](/images/cmds2.png "cmds2")


# Running 24/7

### This is built to be ran 24/7 using docker
**Be sure to CD into your working directory with dockerfile and bot.py within**

```bash
**This is for running locally**

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


```bash
**This is for Runing on remote server**

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


# Build & Push to remote location

### Docker Container
**Make sure you are in the directory that has you Dockerfile and bot script**
```bash
docker build --no-cache -t 10.10.10.1:5000/bot-name .

docker push 10.10.10.1:5000/bot-name
```

## Contributions are welcomed! 💚
**If you have any ideas, talk to me here:  [![Issues][1.4]][2]**
**Or submit an [issue]([1])

**Check out my personal bot account here:  [![Twitter][1.2]][2]**



<!-- link to issues page -->

[1]: https://github.com/abspen1/twitter-bot/issues

<!-- link to messaging webapp page -->

[2]: https://abspen1.github.io/about/contact/contact.html

<!-- links to your social media accounts -->

[2]: https://twitter.com/interntendie

<!-- icons without padding -->

[1.2]: http://i.imgur.com/wWzX9uB.png (twitter icon without padding)
[1.4]: https://i.imgur.com/2SqWbO1.png (mail icon without padding)
