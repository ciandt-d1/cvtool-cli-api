FROM python:3-slim

RUN apt-get update && \
    apt-get install -y git

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir gunicorn
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

CMD gunicorn -w 4 -b 0.0.0.0:8080 run:app
