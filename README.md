# metsis-deploy

[![Join the chat at https://gitter.im/NorDataNet/metsis-deploy](https://badges.gitter.im/NorDataNet/metsis-deploy.svg)](https://gitter.im/NorDataNet/metsis-deploy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

An opinionated list of Docker-based *data-processing* and *data-services* tools.

**Sart the environment**
```
git clone https://github.com/NorDataNet/metsis-deploy
cd metsis-deploy

docker-compose up
```

To deploy the environment, docker-compose will pull the images from dockerhub.
If needed, to build a specific container simply run:

```docker build -t target_name metsis-xxxx/```


List of *containers*:

* [Drupal](metsis-drupal/README.md)
* [PostgreSQL](metsis-postgres/README.md) 
* [SOLR](metsis-solr/README.md) 
* [FastAPI](metsis-fastapi/README.md) 
* [Jupyter](metsis-jupyter/README.md) 
* [PyCSW](metsis-pycsw/README.md) 
* [PyDAP](metsis-pydap/README.md) 
* [PyWPS](metsis-pywps/README.md) 

Note, the default docker-compose.yml will start only the `Drupal`, `PostgreSQL`, `SOLR` and `FastAPI` services required to develop and test the FastAPI based application.
