FROM python:3
ENV PYTHONUNBUFFERED 1
#RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN apt update
RUN apt install -y --no-install-recommends binutils libproj-dev gdal-bin
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_lg
COPY . /code/
COPY src/collaborative_platform/collaborative_platform/settings_template.py /code/src/collaborative_platform/collaborative_platform/settings.py

EXPOSE 8000
STOPSIGNAL SIGINT
ENTRYPOINT ["python", "src/collaborative_platform/manage.py"]
