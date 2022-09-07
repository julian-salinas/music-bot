FROM python:3.9.5

WORKDIR /home/music-bot

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt
