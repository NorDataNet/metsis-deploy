mkdir /tmp/buildfimex
cd /tmp/buildfimex

wget https://cmake.org/files/v3.15/cmake-3.15.0-Linux-x86_64.tar.gz
tar -zxvf cmake-3.15.0-Linux-x86_64.tar.gz

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
/tmp/buildfimex/cmake-3.15.0-Linux-x86_64/bin/cmake ..
make
make install
cd ../..

git clone https://github.com/metno/mi-programoptions
cd mi-programoptions
mkdir build
cd build
/tmp/buildfimex/cmake-3.15.0-Linux-x86_64/bin/cmake ..
make
make install
cd ../..

git clone https://github.com/epifanio/date
cd date
mkdir build
cd build
/tmp/buildfimex/cmake-3.15.0-Linux-x86_64/bin/cmake ..
make
make install
cd ../..

git clone https://github.com/metno/fimex
cd fimex
mkdir build
cd build
/tmp/buildfimex/cmake-3.15.0-Linux-x86_64/bin/cmake \
                                           -Dlibxml2_INC_DIR=/usr/include/libxml2 \
                                           -Dlibxml2_LIB=/usr/lib/x86_64-linux-gnu/libxml2.so \
                                           -Dnetcdf_INC_DIR=/usr/include \
                                           -Dnetcdf_LIB=/usr/lib/x86_64-linux-gnu/libnetcdf.so \
                                           -Dproj_INC_DIR=/usr/include \
                                           -Dproj_LIB=/usr/lib/x86_64-linux-gnu/libproj.so ..
                                                                             
make
make install
rm -rf /tmp/buildfimex


