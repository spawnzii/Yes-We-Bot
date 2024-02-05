FROM python:3-slim-bullseye

RUN apt update && apt upgrade -y && apt install libssl-dev gcc python-dev libldap2-dev libsasl2-dev -y

WORKDIR /app
COPY app/ .
RUN mkdir config

RUN pip3 install -U pip pyopenssl && pip3 install -U -r requirements.txt

ENTRYPOINT [ "python3","-u","main.py" ]
