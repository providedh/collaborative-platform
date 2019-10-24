FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN apt update
RUN apt install -y --no-install-recommends binutils libproj-dev gdal-bin
RUN pip install -r requirements.txt
COPY . /code/

EXPOSE 8000
STOPSIGNAL SIGINT
#ENTRYPOINT ["python", "src/collaborative_platform/manage.py"]
