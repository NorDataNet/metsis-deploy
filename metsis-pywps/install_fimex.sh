cd /tmp/buildfimex
git clone https://github.com/epifanio/fimex
cd fimex
mkdir build
cd build
cmake \
    -Dlibxml2_INC_DIR=/usr/include/libxml2 \
    -Dlibxml2_LIB=/usr/lib/x86_64-linux-gnu/libxml2.so \
    -Dnetcdf_INC_DIR=/usr/include \
    -Dnetcdf_LIB=/usr/lib/x86_64-linux-gnu/libnetcdf.so \
    -Dproj_INC_DIR=/usr/include \
    -Dproj_LIB=/usr/lib/x86_64-linux-gnu/libproj.so ..


make
make install
rm -rf /tmp/buildfimex