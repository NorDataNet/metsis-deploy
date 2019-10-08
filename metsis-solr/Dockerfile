FROM solr:8.2
ENV DEBIAN_FRONTEND=noninteractive

USER root
RUN apt-get update && apt-get install -y mlocate sudo

RUN echo "solr ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/solr && \
    chmod 0440 /etc/sudoers.d/solr

USER solr

ADD myconfig /opt/solr/server/solr/configsets/myconfig
RUN mkdir -p /tmp/data
