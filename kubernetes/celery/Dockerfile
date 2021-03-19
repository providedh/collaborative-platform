FROM python:3

WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_lg
STOPSIGNAL SIGINT

#ENTRYPOINT ["cd /app/src/collaborative_platform && celery -A collaborative_platform worker -B -l DEBUG -E'"]
ENTRYPOINT ["ls /"]
