#7.67-apache
#docker run --name some-drupal -p 8080:80 -d drupal
#from drupal:7.67-apache

from drupal:8.7.10-apache

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y upgrade && apt-get install -y build-essential \
                                         checkinstall \
                                         ruby-dev \
                                         ruby-full \
                                         git \
                                         nano \
                                         vim \
                                         wget \
                                         dash \
                                         mlocate
                                         
RUN gem install compass \
                compass-normalize \
                toolkit \
                susy \
                breakpoint \
                compass-validator \
                singularitygs \
                # rdoc \
                guard \
                guard-livereload \
                zen-grids \
                gist
