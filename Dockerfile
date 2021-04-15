FROM python:3.6-stretch

COPY requirements.txt requirements.txt

RUN pip --trusted-host pypi.org -r requirements.txt

ENV TZ=US/Central
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY bot.py /tmp/bot.py

CMD ["/bin/bash", "-c", "source activate py36 && python -u /tmp/bot.py" ]