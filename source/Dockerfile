FROM python:3.8

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY . /app
WORKDIR /app

ENTRYPOINT ["gunicorn", "app:app", "-b", "0.0.0.0:8001"]