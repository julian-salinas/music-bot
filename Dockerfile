FROM python:3.9.5

WORKDIR /home/grubi

# Actualizar repositorios e instalar ffmpeg
RUN apt-get -y update && \
    apt-get -y install --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*


# Instalar requerimientos
COPY . .
RUN pip install -r requirements.txt

# docker build -t <container-name> .
# docker run -it -v <repo path>:/home/grubi <container-name> bash 