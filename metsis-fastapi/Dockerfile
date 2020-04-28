FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y dist-upgrade && apt-get install -y git

ENV BASKETDIR /opt/basket/

WORKDIR /

COPY ./requirements.txt /requirements.txt

RUN pip3 install -U pip
RUN pip3 install -r requirements.txt
RUN pip3 install git+https://github.com/tiangolo/fastapi

EXPOSE 80
