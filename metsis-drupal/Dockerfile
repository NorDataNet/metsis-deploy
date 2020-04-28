#7.67-apache
#docker run --name some-drupal -p 8080:80 -d drupal
from drupal:7.67-apache

#from drupal:8.7.10-apache

ENV DEBIAN_FRONTEND=noninteractive
RUN for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done

RUN apt-get update && apt-get -y dist-upgrade && apt-get install -y build-essential \
                                         checkinstall \
                                         ruby-dev \
                                         ruby-full \
                                         git \
                                         nano \
                                         vim \
                                         wget \
                                         dash \
                                         mlocate

RUN apt-get install -y curl git unzip postgresql
RUN curl -sS https://getcomposer.org/installer -o composer-setup.php
RUN php composer-setup.php --install-dir=/usr/local/bin --filename=composer
RUN composer global require drush/drush:8.*

ENV PATH="/root/.composer/vendor/bin:${PATH}"

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

RUN drush dl ctools date entity views views_bulk_operations jquery_update
# && drush en ctools
