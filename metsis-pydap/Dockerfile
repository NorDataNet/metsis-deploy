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
RUN apt-get install -y dpkg-dev  \
                       fakeroot  \
                       lintian  \
                       python3-setuptools  \
                       python3-wheel  \
                       python3-pip  \
                       -o APT::Install-Suggests=0 \
                       -o APT::Install-Recommends=0

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

RUN git clone https://github.com/epifanio/webob
RUN cd webob && py2deb \
    --repository=/pkg --name-prefix=python3 .
RUN dpkg -i /pkg/*.deb

#                       python3-webob \

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
RUN echo "####    ####    ####    ####    ####    ####    ####"
# Build a debian package for pydap from git:master
RUN git clone https://github.com/epifanio/pydap
RUN cd pydap && py2deb \
    --use-system-package=numpy,python3-numpy \
    --use-system-package=Webob,python3-webob \
    --use-system-package=Jinja2,python3-jinja2 \
    --use-system-package=docopt,python3-docopt \
    --use-system-package=six,python3-six \
    --use-system-package=beautifulsoup4,python3-bs4 \
    --use-system-package=requests,python3-requests \
    --use-system-package=markupsafe,python3-markupsafe \
    --use-system-package=certifi,python3-certifi \
    --use-system-package=chardet,python3-chardet \
    --use-system-package=idna,python3-idna \
    --use-system-package=soupsieve,python3-soupsieve \
    --use-system-package=urllib3,python3-urllib3 \
    --use-system-package=gunicorn,python3-gunicorn \
    --use-system-package=netcdf4,python3-netcdf4 \
    --use-system-package=paste,python3-paste \
    --use-system-package=pastedeploy,python3-pastedeploy \
    --repository=/pkg --name-prefix=python3 .

# Quick check if the package has been built,
# and copy the contents in the default apache web root directory
# so they can be downloaded
RUN ls /pkg
RUN cp -r /pkg/* /var/www/html/

# installing built pydap package
RUN dpkg -i /pkg/python3-pydap*

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
