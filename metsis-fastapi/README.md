This image provides a WEB API based on the [`fastapi`]() library. It mounts a volume to serve a fastapi-based application

You can run this image as standalone service by running:

```
sudo docker run -p 5000:80 -v 'absolute-path-to'/metsis-deploy/volumes/fastapi/pybasket/config.yaml:/opt/basket/config.yaml -v 'absolute-path-to'/metsis-deploy/volumes/fastapi/pybasket/app:/app epinux/metsis-fastapi
```

Assuming the service is running on `localhost:5000` you can access api API description at `http://localhost:5000/docs#/default`

Assuming a netcdf resource is available at `resource_url` 

Testing of the plotting API based on [`bokeh`]():

* Get list of variables fronm a netcdf resource
    http://localhost:5000/basket/tsplot?get=param&resource_url=resource_url
* Get bokeh plot of a selected variable embedded in a html div `tsplot`
    http://localhost:5000/basket/tsplot?get=plot&resource_url=resource_url&variable=variable_name





