# Hyrax

## Deploy 
To deploy this image, assuming the data to serve via `hyrax` are in the directory:

`/media/volumes/pydap/data`

(notice I am using the same data direvtory for both pydap and hyrax opendap services)

Run the following from the root repository:

```
docker pull epinux/metsis-hyrax
docker run \
       -p 9090:8080 \ 
       -v /path/to/volumes/pydap/data:/var/www/localhost/pydap/data \ 
       epinux/metsis-hyrax
```

The `hyrax` service can be made available on the `localhost` on port `9090` under the path `/opendap`
 
 e.g.: `http://localhost:9090/opendap/`
