# PyBasket
**Prototype API for time-series plot and METSIS basket functionality**

Docker container serving a web application/API based on the [`fastapi`](https://fastapi.tiangolo.com/){:target="_blank"} python software library. 
The fastapi application and its configuration file are loaded at runtime from a mounted volume

To start the service:

```
sudo docker run -p 5000:80 -v 'absolute-path-to'/metsis-deploy/volumes/fastapi/pybasket/config.yaml:/opt/basket/config.yaml -v 'absolute-path-to'/metsis-deploy/volumes/fastapi/pybasket/app:/app epinux/metsis-fastapi
```

Once started, the API description will be available at `http://localhost:5000/docs#/default`

## NetCDF Plotting API

NetCDF data access is based on  [`xarray`](http://xarray.pydata.org/en/stable/){:target="_blank"}.
Plotting routines are based on  [`bokeh`](https://docs.bokeh.org/en/latest/index.html){:target="_blank"}.
Assuming a NetCDF resource is available at `resource_url`

* Get list of variables from a NetCDF resource
    http://localhost:5000/basket/tsplot?get=param&resource_url=resource_url
* Get the bokeh plot of a selected variable embedded in a html div `tsplot`
    http://localhost:5000/basket/tsplot?get=plot&resource_url=resource_url&variable=variable_name

To test the plotting widget is possible to code the API call into an HTML file using `fetch`, see [example](../volumes/fastapi/pybasket/test_ncplot.html){:target="_blank"}.




