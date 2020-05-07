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

Network ports settings:
```
0.0.0.0:8080->80/tcp                                     metsis_drupal8
0.0.0.0:7070->80/tcp                                     metsis_drupal7
80/tcp, 0.0.0.0:444->443/tcp                             metsis_jupyter
0.0.0.0:5432->5432/tcp                                   metsis_postgres
0.0.0.0:8000->8000/tcp                                   metsis_pycsw
8443/tcp, 10022/tcp, 11002/tcp, 0.0.0.0:9090->8080/tcp   hyrax
0.0.0.0:5000->80/tcp                                     metsis_pywps
0.0.0.0:8983->8983/tcp                                   metsis_solr
0.0.0.0:7000->80/tcp                                     metsis_fastapi
```