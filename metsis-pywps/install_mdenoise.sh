wget http://www.cs.cf.ac.uk/meshfiltering/index_files/Doc/mdsource.zip
unzip mdsource.zip
cd mdenoise
g++ -o mdenoise mdenoise.cpp triangle.c
ln -s `pwd`/mdenoise /usr/local/bin/
cd ..
rm -rf mdsource*