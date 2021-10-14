FROM python:3.9.6

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENV TZ=US/Central
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY new_interntendie_tweets.csv /tmp/tweets.csv
COPY bot.py /tmp/bot.py

WORKDIR /tmp/

CMD ["python", "-u", "bot.py"]