#!/usr/bin/env bash

apt-get update
apt-get install -y aptitude -o APT::Force-LoopBreak=1
aptitude safe-upgrade -y
#RUN apt-get -o APT::Force-LoopBreak=1 dist-upgrade -y

apt-get clean && apt-get update && apt-get install -yq --no-install-recommends apt-utils \
    wget \
    bzip2 \
    python3 \
    python3-dev \
    python3-pip \
    ca-certificates \
    sudo \
    locales \
    mlocate \
    libzmq3-dev \
    python3-zmq \
    python3-setuptools \
    openssh-server

echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Install Tini
wget --quiet https://github.com/krallin/tini/releases/download/v0.18.0/tini && \
    echo "12d20136605531b09a2c2dac02ccee85e1b874eb322ef6baf7561cd93f93c855 *tini" | sha256sum -c - && \
    mv tini /usr/local/bin/tini && \
    chmod +x /usr/local/bin/tini