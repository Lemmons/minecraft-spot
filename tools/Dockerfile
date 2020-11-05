FROM python:3.8-slim

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN mkdir -p /srv/spot_tools/

COPY . /srv/spot_tools/
COPY bin/*.py /usr/local/bin/

ENV PYTHONPATH /srv/
