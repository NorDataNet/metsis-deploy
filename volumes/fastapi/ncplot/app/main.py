import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks

try:
    from pydantic.networks import EmailStr
except ImportError:
    from pydantic.types import EmailStr

from app.nc_plot import get_plottable_variables, get_data, create_plot, create_page
from bokeh.embed import components, json_item
import json

from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI, Query, HTTPException

# Adding import for file upload
from typing import List
from fastapi import File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


class Item(BaseModel):
    url: str
    get: str
    variable: str = None

app = FastAPI(title="NC Plot",
              description="Prototype API for plotting, sub-setting and download of NetCDF time-series and 1D profiles.",
              version="0.0.1",
              )


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_PROCESSING_SECOND = 600

app.mount("/static", StaticFiles(directory="./app/static"), name="static")

# files - this method will print the size of uploaded files
@app.post("/files/")
async def create_files(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}

# uploadfiles - this method will print the name of uploaded files
@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}

# exe=ample form 'connected' to the files and 'uploadfiles' API
@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

@app.get("/ncplot/plot")
async def plot(*,
                 resource_url: str = Query(...,title="Resource URL",
                                  description="URL to a netcdf resource"),
                 get: str = Query(...,title="Query string",
                                  description="Receive list of parameters or get the plot, specifying the variable name",
                                  regex='^(param|plot)$'),
                 variable: str = Query(None,
                                       title="Variable name",
                                       description="String with the NetCDF Variable name")):
    if get == 'param':
        return get_plottable_variables(resource_url)

    if get == 'plot':
        if not variable or variable not in get_plottable_variables(resource_url)["y_axis"]:
            raise HTTPException(status_code=404, detail="Variable not found")
        data = get_data(resource_url, variable, resample=None)
        #json_plot = create_plot(data)
        json_plot = create_page(data)
        json_data = json_item(json_plot, target='tsplot')
        #json_data['test'] = "<b>BOLD</b>"
        return json_data
    if get == 'data':
        if not variable or variable not in get_plottable_variables(resource_url)["y_axis"]:
            raise HTTPException(status_code=404, detail="Variable not found")
        data = get_data(resource_url, variable, resample=None)
        return data

