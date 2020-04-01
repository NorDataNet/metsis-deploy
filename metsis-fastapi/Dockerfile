FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y dist-upgrade

ENV BASKETDIR /opt/basket/

WORKDIR /

COPY ./requirements.txt /requirements.txt

RUN pip3 install -U pip
RUN pip3 install -r requirements.txt
RUN pip3 install -U fastapi

EXPOSE 80
