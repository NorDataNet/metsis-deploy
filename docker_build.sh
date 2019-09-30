echo "####################################"
echo "Building image drupal"
echo "####################################"
docker build -t epinux/metsis-drupal metsis-drupal/ # --no-cache
echo "####################################"
echo "Building image postgres"
echo "####################################"
docker build -t epinux/metsis-postgres metsis-postgres/ # --no-cache
echo "####################################"
echo "Building image pybasket"
echo "####################################"
docker build -t epinux/metsis-pybasket metsis-pybasket/ # --no-cache
echo "####################################"
echo "Building image pydap"
echo "####################################"
docker build -t epinux/metsis-pydap metsis-pydap/ # --no-cache
echo "####################################"
echo "Building image pywps"
echo "####################################"
docker build -t epinux/metsis-pywps metsis-pywps/ # --no-cache
echo "####################################"
echo "Building image solr"
echo "####################################"
docker build -t epinux/metsis-solr metsis-solr/ # --no-cache
echo "####################################"
echo "Building image pybasket"
echo "####################################"
docker build -t epinux/metsis-pybasket metsis-pybasket/ # --no-cache
echo "####################################"
echo "Building image pycsw"
echo "####################################"
docker build -t epinux/metsis-pycsw metsis-pycsw/ # --no-cache

