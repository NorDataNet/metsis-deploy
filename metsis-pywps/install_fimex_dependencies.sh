mkdir /tmp/buildfimex
cd /tmp/buildfimex

pip3 install pytest
git clone https://github.com/pybind/pybind11.git 
cd pybind11
mkdir build
cd build
cmake ..
make
make install
cd ../..

git clone https://github.com/metno/mi-cpptest
cd mi-cpptest
mkdir build
cd build
cmake ..
make
make install
cd ../..

git clone https://github.com/metno/mi-programoptions
cd mi-programoptions
mkdir build
cd build
cmake ..
make
make install
cd ../..

git clone https://github.com/epifanio/date
cd date
mkdir build
cd build
cmake ..
make
make install
cd ../..


