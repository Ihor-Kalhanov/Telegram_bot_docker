FROM python:3


COPY requirements.txt ./
RUN apt-get update && apt-get update -y && pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app


COPY . /usr/src/app

CMD [ "python", "main.py" ]