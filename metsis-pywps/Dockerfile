# based on https://hub.docker.com/r/geographica/gdal2/~/dockerfile/
# Using a fat docker since other images like nginx-gunicorn will just incorporate extra services

# FROM phusion/baseimage

FROM debian:sid-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y dist-upgrade

MAINTAINER Jorge S. Mendes de Jesus <jorge.dejesus@protomail.com>

ARG ROOTDIR=/usr/local/ 


ARG PROCESSOR_N=8
ARG FLASK_GIT=https://github.com/epifanio/pywps-flask.git

WORKDIR $ROOTDIR/
# install_clean # apt-get install -y

RUN apt-get update -y && apt-get install -y  \
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
	git \
	cmake \
    wget \
    libudunits2-dev \
    libxml2-dev \
    libproj-dev \
    libnetcdf-dev \
    libcurl4-gnutls-dev \
    pkg-config \
    runit \
    netcdf-bin \
    -o APT::Install-Suggests=0 \
    -o APT::Install-Recommends=0

	#gdal-bin \
	#python3-gdal \
	#grass-core \
    #python3-netcdf4 \

#RUN apt-get --purge remove -y --allow-remove-essential util-linux
#RUN apt-get install -y util-linux

# RUN apt-get update # && \
#     apt-get upgrade -y && \ 
# RUN apt-get install -y libudunits2-dev \
#                      wget \
#                       libxml2-dev \ 
#                       libproj-dev \
#                       libnetcdf-dev \
#                       libcurl4-gnutls-dev \
#                       pkg-config libudunits2-dev

ADD install_fimex_dependencies.sh /tmp/install_fimex_dependencies.sh
RUN /bin/bash /tmp/install_fimex_dependencies.sh

RUN pwd
ADD install_fimex.sh /tmp/install_fimex.sh
RUN /bin/bash /tmp/install_fimex.sh

WORKDIR /

RUN git clone $FLASK_GIT

WORKDIR /pywps-flask

RUN apt-get install -y python3-sqlalchemy \
                       python3-alembic \
                       python3-click \
                       python3-jinja2 \
                       python3-jsonschema \
                       python3-lxml \
                       python3-owslib \
                       python3-dateutil \
                       python3-requests \
                       python3-werkzeug

RUN git clone https://github.com/geopython/pywps && cd pywps && pip3 install . && cd .. && rm -rf pywps
# git+https://github.com/geopython/pywps
RUN pip3 install -r requirements.txt
RUN pip3 install grass-session
RUN pip3 install bokeh
# RUN python3 setup.py build
RUN python3 setup.py install


RUN apt-get install -y apache2 libapache2-mod-wsgi-py3 && a2enmod wsgi
ADD pywps.conf /etc/apache2/sites-enabled/pywps.conf
ADD pywps.wsgi /pywps-flask/wsgi/pywps.wsgi
RUN chmod -R 777 /pywps-flask/logs

RUN apt-get install -y unzip
ADD install_mdenoise.sh /tmp/install_mdenoise.sh
RUN /bin/bash /tmp/install_mdenoise.sh

# cool stuff!
RUN pip3 install git+https://github.com/grantjenks/python-sortedcontainers
RUN pip3 install xmltodict
RUN pip3 install sickle
RUN pip3 install tqdm
RUN pip3 install parmap
RUN pip3 install cython

RUN apt-get install -y \
                       python3-cartopy  \
                       python3-owslib  \
                       python3-pysolr  \
                       -o APT::Install-Suggests=0 \
                       -o APT::Install-Recommends=0

RUN pip3 install xarray
RUN pip3 install holoviews
RUN pip3 install hvplot
RUN pip3 install json2html

RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y \
                    gdal-bin \
	                python3-gdal \
	                grass-core \
	                python3-netcdf4 \
	                python3-geopandas



EXPOSE 80
CMD ["apachectl", "-D", "FOREGROUND", "-e", "info"]
#CMD ["python3", "/pywps-flask/demo.py", "-a"]




