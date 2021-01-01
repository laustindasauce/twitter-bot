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
You can run your bot [locally](/README-local.md), on a [Google Cloud VM instance](/README-cloud.md), or on an [AWS ec2 VM](/README-aws.md). I prefer in the cloud so that I don't have to worry about my computer being on all the time to keep the script running. For the cloud I have instructions for using a Google Cloud Instance below. When you open a new account on the Google Cloud console you will recieve $300 credit for you to spend however you'd like. This will last a long time if the only thing you are doing on the cloud is running the twitter bot.

## Contributions are welcomed! 💚
* **If you have any ideas, talk to me here:  [![Issues][1.4]][2]**
* **Or submit an issue [here](https://github.com/abspen1/twitter-bot/issues)**

* **Check out my personal bot account here:  [![Twitter][1.2]][3]**



<!-- link to issues page -->

[1]: https://github.com/abspen1/twitter-bot/issues

<!-- link to messaging webapp page -->

[2]: https://austinspencer.works/about/contact/

<!-- links to your social media accounts -->

[3]: https://twitter.com/interntendie

<!-- icons without padding -->

[1.2]: http://i.imgur.com/wWzX9uB.png (twitter icon without padding)
[1.4]: https://i.imgur.com/2SqWbO1.png (mail icon without padding)
