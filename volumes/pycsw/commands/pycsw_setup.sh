cd sample_data
if [ ! -f master.zip ]; then
  wget https://github.com/GeoNode/gisdata/archive/master.zip
  unzip master.zip
  python3 /usr/local/bin/pycsw-admin.py -c setup_db -f /etc/pycsw/pycsw.cfg
  python3 /usr/local/bin/pycsw-admin.py -c load_records -f /etc/pycsw/pycsw.cfg -p gisdata-master/gisdata/metadata/good -r
fi

python3 /usr/local/bin/entrypoint.py
# with transaction == True, havesting of wms can be done with:
# python3 /usr/local/bin/pycsw-admin.py -c post_xml -u http://pycsw:8000/pycsw/csw.py -x sample_data/xml/post.xml