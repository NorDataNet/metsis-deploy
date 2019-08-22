docker network create proxy_net
source sample.env
docker-compose up
# docker exec -it --user=solr solr bin/solr create_core -c taxlots

