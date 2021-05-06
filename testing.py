import datetime

def weekly_sentiment():
    bulls = 7
    bears = 6
    split = 2
    total = bulls + bears + split
    week_sentiment = ''
    if bulls > bears:
        week_sentiment = 'bullish'
    elif bears > bulls:
        week_sentiment = 'bearish'
    else:
        week_sentiment = 'nuetral'
    today = datetime.date.today()
    last_monday = str(today - datetime.timedelta(days=today.weekday()))
    today = str(today)
    # timeframe = f"{last_monday} - {today}"
    adjTimeframe = f" {last_monday[-5:]} - {today[-5:]}"
    
    
    to_string = f"From {adjTimeframe} at close there were {total} stock market sentiment readings." + \
    f" Sentiment was {week_sentiment} overall, with {bulls} bullish, {bears} bearish, and {split} nuetral readings."

    # client.hset('stock_sentiment', today, week_sentiment)

    print(to_string)

weekly_sentiment()