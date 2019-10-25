#!/usr/bin/env bash

mkdir toc
cd toc
wget https://raw.githubusercontent.com/minrk/ipython_extensions/master/nbextensions/toc.js
wget https://raw.githubusercontent.com/minrk/ipython_extensions/master/nbextensions/toc.css
cd ..
jupyter-nbextension install toc
jupyter-nbextension enable toc/toc
rm -rf toc
jupyter nbextension install https://rawgithub.com/minrk/ipython_extensions/master/nbextensions/gist.js
jupyter nbextension enable gist

#git clone https://github.com/Jupyter-contrib/jupyter_contrib_core
#cd jupyter_contrib_core
#pip3 install .
#cd ..
#
#
#
#pip install jupyter_nbextensions_configurator
#pip3 install jupyter_nbextensions_configurator
#
#jupyter nbextensions_configurator enable --system
#
#git clone https://github.com/ipython-contrib/jupyter_contrib_nbextensions
#pip install -e jupyter_contrib_nbextensions
#pip3 install -e jupyter_contrib_nbextensions
#
#jupyter contrib nbextension install
#
#
#rm -rf jupyter_contrib_nbextensions

git clone https://github.com/Jupyter-contrib/jupyter_contrib_core
cd jupyter_contrib_core

python3 setup.py install

pip3 install jupyter_nbextensions_configurator

pip3 install https://github.com/ipython-contrib/jupyter_contrib_nbextensions/tarball/master

cd ../
rm -rf jupyter_contrib_core