FROM ubuntu

# RUN apt-get update

# Added
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Instalar python y pip
RUN apt-get install python3 python3-dev -y
RUN apt install python3-pip -y

# Instalar requerimientos
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app

# docker build -t <container-name> .
# docker run -it -v <repo path>:/app <container-name> bash 