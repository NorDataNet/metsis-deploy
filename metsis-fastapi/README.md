A pre-built pybasket image is available on docker-hub

```
docker pull epinux/metsis-pybasket 
```
 
You can run this image as standalone service by running:

```
docker run -p host_port:80 -t epinux/metsis-fastapi -v /absolute/path/to/metsis-deploy/volumes/fastapi/pybasket/config.yaml:/opt/basket/config.yaml 
```
Assuming the service is running on `localhost:5000` you can access api description at `http://localhost:5000/docs#/default`

In case you want to build a new fastapi image simply run:

```
docker build -t 'new_image_name'
```

and do not forget to replace `epinux/metsis-fastapi` with the `new_image_name`


