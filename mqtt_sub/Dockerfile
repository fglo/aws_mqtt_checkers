FROM python:alpine3.7

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD python ./mqtt_sub.py