# =================================================================
#
# Authors: Massimo Di Stefano <massimodsa@met.no>
# Copyright (c) 2017 Ricardo Garcia Silva
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================
#
# Adapted from pycsw official Dockerfile
#
# Contributors:
#   Massimo Di Stefano
#   Arnulf Heimsbakk
#
# Note in the instruction above I added some extra packages:
# git - to clone pydap repo or install with pip directly form github
# bash - for interactive docker session
# xmltodict - pythonic way to work on xml

FROM alpine:3.11
LABEL maintainer="massimods@met.no,aheimsbakk@met.no"

RUN apk add --no-cache \
    bash nano wget sqlite openrc \
    ca-certificates \
    git \
    libxml2 \
    libxslt \
    python3 \
    py3-pip\
    apache2 \
    apache2-ctl \
    apache2-mod-wsgi \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
    && apk add --no-cache netcdf hdf5 \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community

RUN apk add --no-cache --virtual .build-deps \
    build-base \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
    && apk add --no-cache --virtual .build-deps2 netcdf-dev hdf5-dev \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
  && pip3 install --upgrade pip setuptools \
  && pip3 install wheel \
  && pip3 install \
    gunicorn \
    lxml \
    xmltodict \
    chardet \
    certifi \
    bs4 \
    docopt \
    jinja2 \
    markupsafe \
    numpy \
    six \
    requests \
    idna \
    soupsieve \
    urllib3 \
    netcdf4 \
    sqlalchemy \
    gunicorn \
    paste \
    pastedeploy \
    gsw \
    coards \
    ordereddict

RUN cd \
    && git clone https://github.com/epifanio/webob \
    && cd webob \
    && python3 setup.py install \
    && cd \
    && git clone https://github.com/epifanio/pydap \
    && cd pydap \
    && python3 setup.py install \
    && cd \
    && rm -rf webob pydap

# Add netcdf test data

RUN mkdir -p /var/www/localhost/pydap/data
RUN mkdir -p /var/www/localhost/wsgi-bin
# RUN chmod -R 777 /var/www/localhost/wsgi-bin
RUN chmod -R 777 /var/www/localhost/pydap/data

# ADD sample configuration to run pydap as wsgi application under apache
ADD conf/dap.conf /etc/apache2/conf.d/dap.conf
ADD conf/dap.wsgi /var/www/localhost/wsgi-bin/pydap.wsgi

RUN rc-update add apache2 default

EXPOSE 80

RUN apk del .build-deps
RUN apk del .build-deps2

CMD ["apachectl", "-D", "FOREGROUND", "-e", "info"]