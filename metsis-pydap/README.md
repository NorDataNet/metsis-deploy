# How to deploy:

By cloning the [metsis-deploy](https://github.com/NorDataNet/metsis-deploy) repository

`git clone https://github.com/NorDataNet/metsis-deploy`

it is possible to build the `pydap server` only with:

```
cd metsis-deploy/metsis-pydap
docker build -t my_pydap_docker_image_name .
```

once the image is built, assuming the data to serve via `pydap` aere in the directory:


`/media/volumes/pydap/data`

The `pydap` service can be made available on the `localhost` on port `8080` by running:

```
docker run -p 8080:80 -v /media/volumes/pydap/data:/var/www/sites/pydap/server/data -t my_pydap_docker_image_name
```

