# PyDAP

## Deploy 
To deploy this image, assuming the data to serve via `pydap` are in the directory:

`/media/volumes/pydap/data`

Run the following from the root repository:

```
docker pull epinux/metsis-pydap
docker run \
       -p 9999:80 \ 
       -v /path/to/volumes/pydap/data:/var/www/localhost/pydap/data \ 
       epinux/metsis-pydap
```

The `pydap` service can be made available on the `localhost` on port `9999`

Note:
This repo will install a forked version of `pydap` and its dependency `webob` to address an unicode issue for certain metadata. 

