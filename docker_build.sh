echo "####################################"
echo "Building image drupal"
echo "####################################"
docker build -t epinux/metsis-drupal8 metsis-drupal/ ${1}
echo "####################################"
echo "Building image jupyter"
echo "####################################"
docker build -t epinux/metsis-jupyter metsis-jupyter/ ${1}
echo "####################################"
echo "Building image postgres"
echo "####################################"
docker build -t epinux/metsis-postgres metsis-postgres/ ${1}
echo "####################################"
echo "Building image pybasket"
echo "####################################"
docker build -t epinux/metsis-pybasket metsis-pybasket/ ${1}
echo "####################################"
echo "Building image pycsw"
echo "####################################"
docker build -t epinux/metsis-pycsw metsis-pycsw/ ${1}
echo "####################################"
echo "Building image pydap"
echo "####################################"
docker build -t epinux/metsis-pydap metsis-pydap/ ${1}
echo "####################################"
echo "Building image pywps"
echo "####################################"
docker build -t epinux/metsis-pywps metsis-pywps/ ${1}
docker build -t epinux/metsis-pywps-xenial -f metsis-pywps/Dockerfile-xenial metsis-pywps/ ${1}
echo "####################################"
echo "Building image solr"
echo "####################################"
docker build -t epinux/metsis-solr metsis-solr/ ${1}
echo "####################################"
