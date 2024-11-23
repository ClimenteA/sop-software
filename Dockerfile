FROM python:3.12-slim-bullseye

RUN mkdir -p /home/sites
RUN mkdir -p /home/storage
WORKDIR /home/sites

COPY . .

RUN pip3 install -r requirements.txt
