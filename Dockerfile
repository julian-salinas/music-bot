FROM python:3.10.6

WORKDIR /home/music-bot

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "src/bot.py"]
