FROM python:3.8-buster
WORKDIR /data
RUN apt-get update
RUN apt-get install -y vim less
RUN apt-get install -y libsndfile1-dev

RUN pip install --upgrade pip
RUN pip install magenta --no-cache-dir
RUN pip install midi2audio==0.1.1 music21==5.5.0

RUN apt-get install -y fluidsynth