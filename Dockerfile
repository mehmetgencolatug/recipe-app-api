FROM python:3.7-alpine
MAINTAINER Mehmet Gencol inda Django Education

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt


WORKDIR /app
COPY ./app /app

RUN adduser -D mehmetgencol
USER mehmetgencol

