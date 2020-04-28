# Use latest debian unstable
FROM debian:sid-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y dist-upgrade

# Install few extra packages needed to clone repository and run web HTTP services
RUN apt-get install -y git \
                       apache2 \
                       nano \
                       libapache2-mod-wsgi-py3 \
                       build-essential \
                       -o APT::Install-Suggests=0 \
                       -o APT::Install-Recommends=0
# build-eesential is not needed,
# but adding it anyway for many reason.
# is is useful when playing with the image
# and debug packages that requires to be built from src
 
# Install minimal debian python build environment
# lintian  \
RUN apt-get install -y dpkg-dev  \
                       fakeroot  \
                       python3-setuptools  \
                       python3-wheel  \
                       python3-pip  \
                       -o APT::Install-Suggests=0 \
                       -o APT::Install-Recommends=0

# RUN pip3 install --upgrade pip

RUN apt-get remove -y python3-pip && python3.8 -m easy_install pip
# Install py2deb

RUN pip3 install git+https://github.com/paylogic/py2deb

# Add a Directory where to store packages
RUN mkdir /pkg
ADD docker_test/debcontrol.sh /pkg/debcontrol.sh

# Install Pydap dependencies

# Use a webob fork, as the actual version is buggy
# it fails in serving netcdf files via pydap
# when the description has unicode characters in it
# see issue on github [https://github.com/pydap/pydap/issues/196]



RUN apt-get install -y python3-chardet \
                       python3-certifi \
                       python3-bs4 \
                       python3-docopt \
                       python3-jinja2 \
                       python3-markupsafe \
                       python3-numpy \
                       python3-six python3-requests \
                       python3-idna \
                       python3-soupsieve \
                       python3-urllib3 \
                       python3-netcdf4 \
                       python3-sqlalchemy \
                       python3-gunicorn \
                       python3-paste \
                       python3-pastedeploy \
                       -o APT::Install-Suggests=0 -o APT::Install-Recommends=0

RUN cd && git clone https://github.com/epifanio/webob && cd webob && python3 setup.py install

RUN cd && git clone https://github.com/epifanio/pydap && cd pydap && python3 setup.py install



RUN ls /pkg
RUN cp -r /pkg/* /var/www/html/

# Add netcdf test data
RUN mkdir -p /var/www/sites/pydap/server/data
#ADD docker_test/SN99938.nc /var/www/sites/pydap/server/data/SN99938.nc

# ADD sample configuration to run pydap as wsgi application under apache
ADD docker_test/dap.conf /etc/apache2/sites-enabled/dap.conf
ADD docker_test/dap.wsgi /var/www/pydap/server/apache/pydap.wsgi

RUN update-rc.d apache2 defaults
EXPOSE 80

# Clean up APT
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


CMD ["apachectl", "-D", "FOREGROUND", "-e", "info"]
# fpm -e --after-install ../DEBIAN/postinst.new -s deb -t deb ../old.deb
