# Jupyter

Container based on linux alpine running a jupyter notebook with a python-3.8.2 kernel and ssl encryption enabled.
(docker environment based on the [nbgallery](https://github.com/nbgallery/jupyter-alpine) repository)

Some of the Python packages pre-installed includes:

```
    numpy 
    xarray 
    netCDF4 
    bokeh 
    pandas 
    json2html 
    requests
``` 

The configuration file for the notebook sets ```c.NotebookApp.notebook_dir = 'notebooks'``` as working directory for the notebooks.


To start the service:

```
sudo docker run -p 444:443 -v 'absolute-path-to'/metsis-deploy/volumes/jupyter/notebooks:/root/notebooks/ epinux/metsis-jupyter
```

Note, keep an eye on the notebook logs as you may require to copy and use the access token to log-into the jupyter environment and set a new password.