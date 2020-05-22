# =================================================================
#
# Authors: Massimo Di Stefano <massimods@met.no>
# Copyright (c) 2020 Massimo Di Stefano
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
# Adapted from pycsw official Dockerfile and from https://github.com/nbgallery/jupyter-alpine
#
# Contributors:
#   Massimo Di Stefano
#


FROM alpine:3.11
LABEL maintainer="massimods@met.no"

EXPOSE 80 443
WORKDIR /root

ENV CPPFLAGS=-s \
    SHELL=/bin/bash

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["jupyter-notebook-secure"]

COPY util/* /usr/local/bin/
COPY config/bashrc /root/.bashrc

# add edge repository for geospatial libs when/if needed
# COPY config/repositories /etc/apk/repositories

COPY config/*.rsa.pub /etc/apk/keys/

RUN min-apk \
    bash \
    wget \
    nano \
    ca-certificates \
    git \
    python3 \
    sqlite \
    zeromq \
    tini \
    bzip2 \
    libressl \
    openssh-client \
    binutils \
    openssl \
    proj \
    proj-util \
    geos \
    freetype \
    graphviz \
    libxml2 \
    libxslt \
    ttf-freefont \
    netcdf \
    hdf5 \
    gdal  \
    py3-pip \
    py3-pygments \
    py3-cffi \
    py3-cryptography \
    py3-jinja2 \
    py3-openssl \
    py3-pexpect \
    py3-tornado \
    py3-pillow \
    py3-numpy \
    py3-scipy \
    py3-pandas \
    py3-geojson \
    py3-lxml \
    py3-gdal \
    py3-shapely \
    py3-rasterio \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community

RUN apk add --no-cache --virtual .build-deps \
        build-base \
        python3-dev \
        zeromq-dev \
        libffi-dev \
        proj-dev \
        geos-dev \
        freetype-dev \
        libxml2-dev \
        libxslt-dev \
        netcdf-dev \
        hdf5-dev \
        py3-numpy-dev \
        gdal-dev \
        --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
        --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
    && pip3 install --upgrade pip setuptools \
    && pip3 install wheel \
    && pip3 install \
        notebook \
        jupyter \
        ipywidgets \
        xarray \
        netCDF4 \
        bokeh \
        json2html \
        requests \
        pygeometa \
        owslib \
        itsdangerous \
        pysolr \
        xmltodict \
        prov \
        shortid \
        pydot \
        cartopy \
        rdflib \
        rdflib-jsonld \
    && jupyter nbextension enable --py --sys-prefix widgetsnbextension


RUN apk del .build-deps &&  \
    echo "### Cleanup unneeded files" && \
    rm -rf /usr/lib/python3*/*/tests && \
    rm -rf /usr/lib/python3*/ensurepip && \
    rm -rf /usr/lib/python3*/idlelib && \
    rm -f /usr/lib/python3*/distutils/command/*exe && \
    rm -rf /usr/share/man/* && \
    clean-pyc-files /usr/lib/python3*

RUN mkdir notebooks

COPY config/jupyter /root/.jupyter/

ADD kernels /usr/share/jupyter/kernels