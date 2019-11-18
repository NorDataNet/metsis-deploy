# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

FROM debian:sid-slim

MAINTAINER Massimo Di Stefano  <epiesasha@me.com>

USER root

# Install all OS dependencies for notebook server that starts but lacks all
# features (e.g., download as all possible file formats)
ENV DEBIAN_FRONTEND noninteractive

ADD scripts/system_upgrade.sh /tmp/system_upgrade.sh
RUN chmod ugo+rx /tmp/system_upgrade.sh; sync; /tmp/system_upgrade.sh

# Configure environment
ENV SHELL /bin/bash
ENV NB_USER metsis
ENV NB_UID 1000
ENV HOME /home/$NB_USER
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Create epinux user with UID=1000 and in the 'users' group
RUN useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && \
    mkdir -p /opt/ && \
    chown $NB_USER  /opt/

USER metsis

# Setup metsis home directory
RUN mkdir /home/$NB_USER/work && \
    mkdir /home/$NB_USER/.jupyter && \
    mkdir -p -m 700 /home/$NB_USER/.local/share/jupyter && \
    echo "cacert=/etc/ssl/certs/ca-certificates.crt" > /home/$NB_USER/.curlrc

USER root

# Install JupyterHub to get the jupyterhub-singleuser startup script
ADD scripts/install_jupyter.sh /tmp/install_jupyter.sh
RUN chmod ugo+rx /tmp/install_jupyter.sh; sync; /tmp/install_jupyter.sh

# Configure container startup as root
EXPOSE 8888
WORKDIR /home/$NB_USER/work
ENTRYPOINT ["tini", "--"]
CMD ["start-notebook.sh"]

# Add local files as late as possible to avoid cache busting
COPY scripts/start.sh /usr/local/bin/
COPY scripts/start-notebook.sh /usr/local/bin/
COPY scripts/start-singleuser.sh /usr/local/bin/
COPY scripts/jupyter_notebook_config.py /home/$NB_USER/.jupyter/
RUN chown -R $NB_USER:users /home/$NB_USER/.jupyter

# Switch back to epinux to avoid accidental container runs as root

ADD scripts/set_passwd.sh /tmp/set_passwd.sh
RUN chmod ugo+rx /tmp/set_passwd.sh; sync; /tmp/set_passwd.sh

# start jupyter installing jupyter extension amd relative build tools

#RUN ln -s /usr/bin/x86_64-linux-gnu-cpp /usr/bin/x86_64-linux-gnu-gcc
RUN apt-get clean && apt-get update && \
    apt-get install -y --no-install-recommends \
    ruby-dev rubygems libmagickwand-dev git nodejs npm curl gnupg

RUN npm install -g npm
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update && apt-get install -y yarn

RUN gem install gist

RUN pip3 install bash_kernel && pip3 install ivisual # && pip3 install octave_kernel && pip3 install jq && pip install jq
RUN pip3 install -U matplotlib
RUN pip3 install -U bokeh
RUN pip3 install pythreejs
# python3 -m octave_kernel.install
RUN python3 -m bash_kernel.install && jupyter nbextension enable --py pythreejs --sys-prefix

ADD scripts/install_nb_extensions.sh /tmp/install_nb_extensions.sh
RUN chmod ugo+rx /tmp/install_nb_extensions.sh; sync; /tmp/install_nb_extensions.sh

RUN pip3 install RISE
RUN jupyter-nbextension install rise --py --sys-prefix
RUN jupyter-nbextension enable rise --py --sys-prefix
RUN jupyter serverextension enable --py jupyterlab --sys-prefix

RUN pip3 install pdvega
RUN jupyter nbextension install --sys-prefix --py vega3

RUN pip3 install qgrid
RUN jupyter nbextension enable --py --sys-prefix qgrid

RUN pip3 install ipywidgets
RUN jupyter nbextension enable --py widgetsnbextension

RUN pip3 install ipympl
RUN jupyter nbextension enable --py --sys-prefix ipympl

RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager

# ADD scripts/install_lab_extensions.sh /tmp/install_lab_extensions.sh
# RUN chmod ugo+rx /tmp/install_lab_extensions.sh; sync; /tmp/install_lab_extensions.sh

RUN pip3 install ipyleaflet
RUN jupyter nbextension enable --py --sys-prefix ipyleaflet
RUN jupyter labextension install jupyter-leaflet

RUN jupyter labextension install jupyterlab-drawio
RUN jupyter labextension install jupyterlab_bokeh
RUN jupyter labextension install @jupyterlab/toc
RUN pip3 install voila
RUN jupyter labextension install @jupyter-voila/jupyterlab-preview
RUN jupyter labextension install @krassowski/jupyterlab_go_to_definition

RUN pip3 install git+https://github.com/psf/black
# RUN pip3 install rpy2 r-formatr
RUN jupyter labextension install @ryantam626/jupyterlab_code_formatter
RUN pip3 install jupyterlab_code_formatter
RUN jupyter serverextension enable --py jupyterlab_code_formatter

RUN pip3 install --upgrade jupyterlab-git
RUN jupyter labextension install @jupyterlab/github
RUN pip3 install jupyterlab_github
RUN jupyter serverextension enable --sys-prefix jupyterlab_github

# fasta-extension:
RUN jupyter labextension install @jupyterlab/fasta-extension
# geojson-extension:
RUN jupyter labextension install @jupyterlab/geojson-extension
# mathjax3-extension:
RUN jupyter labextension install @jupyterlab/mathjax3-extension
# vega2-extension:
# RUN jupyter labextension install @jupyterlab/vega2-extension
# vega3-extension:
RUN jupyter labextension install @jupyterlab/vega3-extension

RUN pip3 install dash jupyterlab-dash
RUN jupyter labextension install jupyterlab-dash

RUN pip3 install ipysheet
RUN jupyter labextension install ipysheet

RUN pip3 install ipyparallel
RUN ipcluster nbextension enable

RUN jupyter nbextension install --sys-prefix --py ipyparallel
RUN jupyter nbextension enable --sys-prefix --py ipyparallel
RUN jupyter serverextension enable --sys-prefix --py ipyparallel

RUN apt install -y texlive node-katex
RUN pip3 install jupyterlab_latex
RUN jupyter labextension install @jupyterlab/latex
# katex-extension:
RUN jupyter labextension install @jupyterlab/katex-extension

RUN jupyter lab build

RUN chmod -R 777 /home/metsis/*
RUN chown -R metsis:$(id -gn metsis) /home/metsis/.config
RUN chown -R metsis:$(id -gn metsis) /home/metsis/.jupyter

USER metsis

RUN jupyter nbextensions_configurator enable --user
RUN jupyter contrib nbextension install --user

RUN jupyter nbextension enable tree-filter/index && \
jupyter nbextension enable collapsible_headings/main && \
jupyter nbextension enable hide_input_all/main && \
jupyter nbextension enable codefolding/edit && \
jupyter nbextension enable codefolding/main


# Install python libraries to develop scientific  use cases

# Install minimal debian python build environment

USER root

RUN apt-get install -y python3-setuptools  \
                       python3-wheel  \
                       python3-pip  \
                       -o APT::Install-Suggests=0 \
                       -o APT::Install-Recommends=0

# Webob
RUN pip3 install git+https://github.com/epifanio/webob
# PyDAP
RUN pip3 install git+https://github.com/epifanio/pydap
# datashader
RUN pip3 install fastparquet
RUN pip3 install git+https://github.com/pyviz/datashader
RUN jupyter labextension install @pyviz/jupyterlab_pyviz

# cool stuff!
RUN pip3 install git+https://github.com/grantjenks/python-sortedcontainers
RUN pip3 install xmltodict
USER metsis

# this directory is mounted as volume to serve static html using the apache server running on the pydap container

RUN mkdir /home/metsis/work/html
