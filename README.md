# Twitter Bot [![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fabspen1%2Ftwitter-bot&count_bg=%2300ACEE&title_bg=%23555555&icon=twitter.svg&icon_color=%2300ACEE&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
Learning python using tweepy and twitter API to automate twitter functions. Some functions used in this are automatically tweeting, replying to mentions, following users back and more. Most of the examples I've seen online were reading and writing from files, however, in my opinion Redis database is as easy, if not easier, to use. Redis also lowers CPU storage space, especially while doing the sentiment analysis which can download thousands of tweets. For more reliable 24/7 running, I built this script into a Docker container. 

## Checkout the [webpage](https://austinspencer.works/twitter-bot/) for some statistics of my account!

# Prerequisites

## Twitter Developer Setup
* Create your developer account [here](https://developer.twitter.com/en/apply-for-access) 
  * [guide](https://developer.twitter.com/en/docs/twitter-api/getting-started/guide)
* Start a new application and fill out your information
* Save your needed keys
  * Consumer ID (API KEY V2)
  * Consumer Secret Key (API SECRET V2)
  * Key ID (ACCESS TOKEN V2)
  * Secret Key ID (SECRET V2)


## IDE/Text Editor
I use Visual Studio Code and prefer that over the other editors I have used. But I will also link some other popular ones if you want to check them out.
* [VSCode](https://code.visualstudio.com/)
* [Sublime](https://www.sublimetext.com/3)
* [PyCharm](https://www.jetbrains.com/pycharm/download/)

## Python Download
Make sure to download a version of Python that is at least 3.
* Download python (3.x) from [here](https://www.python.org/downloads/)

## Customize Your Bot
Below are some instruction you can copy and paste in your terminal to get started with creating your personal bot. First open terminal and then cd into wherever you want to store your code. In this example I will cd into Documents and assume you are using VSCode.
```bash
cd Documents/
git clone https://github.com/abspen1/twitter-bot.git
cd twitter-bot/
# code . is a shortcut with Visual Studio Code that will open the editor with whatever folder you're currently in. If you aren't using VSCode just open the twitter-bot folder from within your editor.
code .
```
Now that you have the code on your local machine you can edit bot.py to make it your own.
Also, if you need inspiration or a live example run the command below in your terminal.
```bash
# cd into twitter-bot folder first
git checkout coding-specific
```
Now you will be able to see the exact script that my twitter bot is running within bot.py.
* After you've personalized the script, you are ready to get it running

## Choose where to run your script
You can run your bot [locally](https://github.com/abspen1/twitter-bot/blob/master/README.md#running-locally) or within a [Google Cloud VM instance](https://github.com/abspen1/twitter-bot/blob/master/README.md#running-on-google-cloud-vm-instance). I prefer in the cloud so that I don't have to worry about my computer being on all the time to keep the script running. For the cloud I have instructions for using a Google Cloud Instance below. When you open a new account on the Google Cloud console you will recieve $300 credit for you to spend however you'd like. This will last a long time if the only thing you are doing on the cloud is running the twitter bot.






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

## Docker Setup
* Mac [instructions](https://www.robinwieruch.de/docker-macos)
* Windows [instructions](https://docs.docker.com/docker-for-windows/install/)


## Build and Run Docker Images
* Be sure to CD into your working directory with dockerfile and bot.py within**
* Export your variables so you can access them with os.getenv() (Mac OS)
```bash
export CONSUMER_KEY="your key" \
&& export CONSUMER_SECRET="your secret" \
&& export SECRET="your secret"\
&& export HOST="external ip address" \
&& export REDIS_PASS="your redis password"\
&& export KEY="your key"
```

```bash
$ docker build twitter-bot

$ docker run -d \
  --name bot_name \
  --restart unless-stopped \
  -e CONSUMER_KEY="some consumer ID" \
  -e CONSUMER_SECRET="some consumer secret KEY" \
  -e KEY="some key ID" \
  -e SECRET="some secret key ID" \
  -e HOST="external ip address" \
  -e REDIS_PASS="some password" \
  -v $PWD:/work \
  twitter-bot
```

**Pull from previous build**
```bash
docker pull bot-name \
&& docker run -d \
  --name bot_name \
  --restart unless-stopped \
  -e CONSUMER_KEY="some consumer ID" \
  -e CONSUMER_SECRET="some consumer secret KEY" \
  -e KEY="some key ID" \
  -e SECRET="some secret key ID" \
  -e HOST="external ip address" \
  -e REDIS_PASS="some password" \
  10.10.10.1:5000/bot-name
```

## Build & Push to remote portainer

### Docker Container
**Make sure you are in the directory that has your Dockerfile and bot script**
```bash
docker build --no-cache -t 10.0.0.1:PORT/bot-name .

docker push 10.0.0.1:PORT/bot-name
```

# Running on Google Cloud VM Instance
* First you need to set up your Google Cloud Instance
* When you set up a cloud account you will get $300 credit!
* You will need to go to [Google Cloud Platform](https://cloud.google.com/gcp/?utm_source=google&utm_medium=cpc&utm_campaign=na-US-all-en-dr-skws-all-all-trial-b-dr-1009135&utm_content=text-ad-none-any-DEV_c-CRE_109860918967-ADGP_Hybrid+%7C+AW+SEM+%7C+SKWS+%7C+US+%7C+en+%7C+Multi+~+Cloud-KWID_43700009609890930-kwd-19383198255&utm_term=KW_%2Bcloud-ST_%2Bcloud&&gclid=Cj0KCQjwv7L6BRDxARIsAGj-34qcziciZyZZMes6maVVBfg7lmWjgqQkUNXdwg8lHqQwTPVtNEWX0xoaAgGPEALw_wcB)
* Then to console where you can set up your compute engine
* Watch this video for help with inital setup [video](https://www.youtube.com/watch?v=p5wl1s5gKY0)
* You should only need machine-type f1-micro (1 vCPU, 0.6 GB memory)
  * **This will help make your $300 credit last longer**
## ssh into your vm instance
* I prefer to do this on my local machine but you can also do it in browser within a shell
* Install gcloud sdk on your local machine.. steps are [here](https://cloud.google.com/sdk/docs/downloads-interactive)
 * There will be a generated ssh that you can copy and paste into your terminal to ssh into your vm instance using gcloud
![Alt text](/images/ssh.png "ssh")
* Once you're inside your instance within your terminal it should look something like this
![Alt text](/images/terminal.png "instance")
## Download Redis
* Awesome instructions [here](https://cloud.google.com/community/tutorials/setting-up-redis)
* Very easy and can be completed in < 10 minutes
* Be sure to create a secure password if you choose to configure remote access (recommended >= 32 characters)
* Find your external IP on your VM console (needed for the HOST env variable)
## Download Docker
* Awesome instructions [here](http://docs.h2o.ai/driverless-ai/latest-stable/docs/userguide/install/google-docker-container.html)
* My tl;dr instructions are below
* Note that you will likely need to add sudo infront of each command
  * Quickest way to fix this when you get the permission denied error
  * $ sudo !!
  * This is a shortcut to run previous command but with super user permissions
```bash
# SCRIPT FOR CPUs ONLY
apt-get -y update

# If you have issues with this command, omit python-software-properties
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
## Clone your git repository to run within docker
* First check that git is installed
* $ git --version
* $ git clone https://github.com/abspen1/twitter-bot.git
* $ ls (check that the repo cloned into your instance)

## Build the docker image
* cd into twitter-bot directory
* $ sudo docker build -t bot .

## Check if image was created
$ sudo docker image ls

## Run docker image in a container
```bash
$ sudo docker run -d \
  --name bot_name \
  --restart unless-stopped \
  -e CONSUMER_KEY="some consumer ID" \
  -e CONSUMER_SECRET="some consumer secret KEY" \
  -e KEY="some key ID" \
  -e SECRET="some secret key ID" \
  -e HOST="external ip address" \
  -e REDIS_PASS="some password" \
  -v $PWD:/work \
  bot
```

## Check that the container is running
* $ sudo docker container ls
* $ sudo docker logs bot_name


## Google Cloud Terminal Commands
![Alt text](/images/cmds1.png "cmds1")
![Alt text](/images/cmds2.png "cmds2")

## Contributions are welcomed! 💚
* **If you have any ideas, talk to me here:  [![Issues][1.4]][2]**
* **Or submit an [issue]([1])**

* **Check out my personal bot account here:  [![Twitter][1.2]][2]**



<!-- link to issues page -->

[1]: https://github.com/abspen1/twitter-bot/issues

<!-- link to messaging webapp page -->

[2]: https://abspen1.github.io/about/contact/contact.html

<!-- links to your social media accounts -->

[2]: https://twitter.com/interntendie

<!-- icons without padding -->

[1.2]: http://i.imgur.com/wWzX9uB.png (twitter icon without padding)
[1.4]: https://i.imgur.com/2SqWbO1.png (mail icon without padding)
