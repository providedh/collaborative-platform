FROM python:3
ENV PYTHONUNBUFFERED 1
RUN apt update
RUN apt install -y --no-install-recommends binutils libproj-dev gdal-bin
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_lg
EXPOSE 8000
STOPSIGNAL SIGINT

WORKDIR /code
COPY . /code/
ENTRYPOINT ["bash startup.sh"]
