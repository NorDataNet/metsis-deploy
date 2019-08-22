FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

ENV BASKETDIR /opt/basket/

WORKDIR /

COPY ./requirements.txt /requirements.txt

RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

COPY ./app /app

EXPOSE 80
