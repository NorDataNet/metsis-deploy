#based on https://hub.docker.com/r/geographica/gdal2/~/dockerfile/
#Using a fat docker since other images like nginx-gunicorn will just incorporate extra services
FROM phusion/baseimage
MAINTAINER Jorge S. Mendes de Jesus <jorge.dejesus@protomail.com>

ARG ROOTDIR=/usr/local/ 


ARG PROCESSOR_N=8
ARG FLASK_GIT=https://github.com/epifanio/pywps-flask.git

WORKDIR $ROOTDIR/

RUN apt-get update -y && install_clean \
	software-properties-common \
	build-essential \
	python3-dev \
	python3-numpy \
	python3-lxml \
	python3-lxml \
	python3-pip \
	python3-wheel \
	python3-setuptools \
	sqlite3 \
	gdal-bin \
	python3-gdal \
	grass-core \
	git \
	cmake

RUN apt-get update && \
    apt-get upgrade -y && \ 
    apt-get install -y libudunits2-dev \
                       wget \
                       libxml2-dev \ 
                       libproj-dev \
                       libnetcdf-dev
                       
ADD install_fimex.sh /tmp/install_fimex.sh
RUN /bin/bash /tmp/install_fimex.sh

WORKDIR /

RUN git clone $FLASK_GIT

WORKDIR /pywps-flask

RUN pip3 install git+https://github.com/geopython/pywps
RUN pip3 install -r requirements.txt

# RUN python3 setup.py build
RUN python3 setup.py install

RUN mkdir /etc/service/pywps4
COPY pywps4_service.sh /etc/service/pywps4/run
RUN chmod +x /etc/service/pywps4/run

EXPOSE 5000

#docker build -t pywps/flask-ubuntu:latest . 
#docker run -p 5000:5000 pywps/flask-ubuntu
#http://localhost:5000/wps?request=GetCapabilities&service=WPS
#http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0    




