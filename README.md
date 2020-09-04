# Twitter Bot Implementing Redis Database (coding branch)
Learning python using tweepy and twitter API to automate twitter functions. Some functions used in this are automatically tweeting, replying to mentions, following users back and more. Most of the examples I've seen online were reading and writing from files, however, in my opinion redis is as easy, if not easier, to use. Redis also lowers CPU storage space, especially while doing the sentiment analysis which can download thousands of tweets. Redis also works really well with Docker which is how this script will be ran 24/7. This branch will use programming keywords to try to get followers interested in programming.


## Sentiment Analysis
Awesome function that can get the sentiment of tweets with specific keywords within them. You download as many tweets as you want and use whatever keyword. I am using the 'stock market' as keyword in this script and downloading 3000 tweets with the keyword in it. Once downloaded there are a few helper functions that will clean up the tweet, removing any extras such as links and 'RT' for retweets. Then using the TextBlob package we can get the polarity and subjectivity of each tweet. Subjectivity is fact/opinion so I am filtering out any with subjectivity > 0.5 (highly opinionated).

## Sentiment Analysis Accuracy
The accuracy for our twitter sentiment analysis has been added. Pretty easy implementation using Alpaca's tradeapi package. What I'm doing is saving the dates where sentiment is bullish and the dates where sentiment is bearish into their respective redis sets. Since the market goes up over time I am weighing bullish heavier than bearish. What I mean by that –– there are multiple reading per day, if one of those readings is bullish then we are considering the overall sentiment for the day bullish. The only way a day can be bearish is if each reading during that day is bearish. After that we are using SPY pricing to consider whether the day was positive or negative. If we overall bullish on the day then what I'm expecting is a positive day the next day, opposite if bearish. When correct we are incrementing global variable 'correct' and when we are incorrect we are incrementing global variable 'wrong'. Then we just sum the two and divide correct by the sum to get our accuracy. 
### Upgrades / To Do
I need to eventually move the global variables into redis key/value pairs and remove the dates once the accuracy is figured. This way I don't need to iterate through each date every time I calculate the accuracy. Instead, we would at most have 2 dates in our sets and the correct and wrong values would be stored in redis so no need to calculate each time.


# Prerequisites
Check master branch


## Contributions are welcomed! 💚
**If you have any ideas, talk to me here:  [![Issues][1.4]][1]**

**Check out my personal bot account here:  [![Twitter][1.2]][2]**



<!-- link to issues page -->

[1]: https://github.com/abspen1/twitter-bot/issues

<!-- links to your social media accounts -->

[2]: https://twitter.com/interntendie

<!-- icons without padding -->

[1.2]: http://i.imgur.com/wWzX9uB.png (twitter icon without padding)
[1.4]: https://i.imgur.com/2SqWbO1.png (mail icon without padding)
