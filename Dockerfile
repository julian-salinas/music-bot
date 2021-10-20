FROM alpine:3.10

RUN apk add --no-cache python3-dev \
    && pip3 install --upgrade pip

WORKDIR /app

COPY . /app

RUN apk add --no-cache ffmpeg

RUN pip3 install -r requirements.txt


CMD ["python3", "src/bot.py"]
