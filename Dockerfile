FROM python
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 80
EXPOSE 443

CMD ["python", "src/collaborative_platform/manage.py", "makemigrations"]
CMD ["python", "src/collaborative_platform/manage.py", "migrate"]
CMD ["python", "src/collaborative_platform/manage.py", "runserver"]
