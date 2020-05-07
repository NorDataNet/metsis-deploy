#
# example: ./docker_build.sh --no-cache --compress --squash --force-rm
#
echo "####################################"
echo "Building image drupal"
echo "####################################"
docker build -t epinux/metsis-drupal metsis-drupal/ ${1} ${2} ${3} ${4}
docker build -f Dockerfile-drupal8 -t epinux/metsis-drupal metsis-drupal8/ ${1} ${2} ${3} ${4}
echo "####################################"
echo "Building image jupyter"
echo "####################################"
docker build -t epinux/metsis-jupyter metsis-jupyter/ ${1} ${2} ${3} ${4}
echo "####################################"
echo "Building image postgres"
echo "####################################"
docker build -t epinux/metsis-postgres metsis-postgres/ ${1} ${2} ${3} ${4}
echo "####################################"
echo "Building image fastapi"
echo "####################################"
docker build -t epinux/metsis-fastapi metsis-fastapi/ ${1} ${2} ${3} ${4}
echo "####################################"
echo "Building image pycsw"
echo "####################################"
docker build -t epinux/metsis-pycsw metsis-pycsw/ ${1} ${2} ${3} ${4}
echo "####################################"
echo "Building image pydap"
echo "####################################"
docker build -t epinux/metsis-pydap metsis-pydap/ ${1} ${2} ${3} ${4}
echo "####################################"
echo "Building image pywps"
echo "####################################"
docker build -t epinux/metsis-pywps metsis-pywps/ ${1} ${2} ${3} ${4}
echo "####################################"
echo "Building image solr"
echo "####################################"
docker build -t epinux/metsis-solr metsis-solr/ ${1} ${2} ${3} ${4}
echo "####################################"
