FROM alpine:3.11
LABEL maintainer="massimods@met.no"

COPY util/* /usr/local/bin/
COPY config/bashrc /root/.bashrc

RUN min-apk \
    bash \
    wget \
    nano \
    python3 \
    sqlite \
    bzip2 \
    python3 \
    py3-jinja2 \
    py3-pillow \
    py3-cffi \
    py3-aiofiles \
    py3-certifi \
    py3-click \
    py3-chardet \
    py3-dnspython \
    py3-email-validator \
    py3-idna \
    py3-itsdangerous \
    py3-six \
    py3-urllib3 \
    py3-simplejson \
    binutils \
    openssl \
    proj \
    proj-util \
    && apk add --no-cache netcdf hdf5 --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing

RUN apk add --no-cache --virtual .build-deps \
    build-base \
    python3-dev \
    libffi-dev \
    proj-dev \
    geos-dev \
    && apk add --no-cache --virtual .build-deps2 netcdf-dev hdf5-dev --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    && pip3 install --upgrade pip setuptools \
    && pip3 install wheel \
    && pip3 install pyproj \
    uvicorn \
    gunicorn \
    numpy \
    xarray \
    netCDF4 \
    bokeh \
    pandas \
    fsspec \
    h5py \
    json2html \
    requests \
    owslib \
    aniso8601 \
    confuse \
    dataclasses \
    graphene \
    graphql-core \
    graphql-relay \
    h11 \
    httptools \
    MarkupSafe \
    OWSLib \
    promise \
    pydantic \
    pyproj \
    python-dateutil \
    python-multipart \
    pytz \
    PyYAML \
    requests \
    Rx \
    starlette \
    ujson \
    uvicorn \
    uvloop \
    websockets \
    pandas \
    bokeh \
    numpy \
    netcdf4 \
    xarray \
    json2html \
    fastapi \
    && apk del .build-deps && apk del .build-deps2 && \
    echo "### Cleanup unneeded files" && \
    rm -rf /usr/lib/python3*/*/tests && \
    rm -rf /usr/lib/python3*/ensurepip && \
    rm -rf /usr/lib/python3*/idlelib && \
    rm -f /usr/lib/python3*/distutils/command/*exe && \
    rm -rf /usr/share/man/* && \
    clean-pyc-files /usr/lib/python3*

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

COPY ./app /app

ENV BASKETDIR /opt/basket/

WORKDIR /

ENV PYTHONPATH=/app

EXPOSE 80

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]