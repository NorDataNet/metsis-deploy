import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pathlib import Path
try:
    from pydantic.networks import EmailStr
except ImportError:
    from pydantic.types import EmailStr

from app.nc_plot import get_plottable_variables, create_page
from app.utils import get_data
from bokeh.embed import components, json_item
import json

from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI, Query, HTTPException

# Adding import for file upload
from typing import List
from fastapi import File, UploadFile, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import os
from fastapi.responses import StreamingResponse
from pathlib import Path

def getstaticfolder():
    current_file = Path(__file__)
    current_file_dir = current_file.parent
    project_root = current_file_dir.parent
    project_root_absolute = project_root.resolve()
    static_root_absolute = project_root_absolute / "static"
    return static_root_absolute

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
                 resource_url: str = Query(...,
                                           title="Resource URL",
                                           description="URL to a netcdf resource"),
                 get: str = Query(...,
                                  title="Query string",
                                  description="Receive list of parameters or get the plot, specifying the variable name",
                                  regex='^(param|plot|data)$'),
                 variable: str = Query(None,
                                       title="Variable name",
                                       description="String with the NetCDF Variable name"),
                 output_format: str = Query(None,
                                            title="output format",
                                            description="output format",
                                            regex='^(csv|nc)$')):
    if get == 'param':
        return get_plottable_variables(resource_url)

    if get == 'plot':
        data = get_data(resource_url, variable)
        # json_plot = create_plot(data)
        json_plot = create_page(data)
        json_data = json_item(json_plot, target='tsplot')
        return json_data
    # https://github.com/tiangolo/fastapi/issues/376
    # probably a good way to find out the root path for the app
    # current_file = Path(__file__)
    # current_file_dir = current_file.parent
    # project_root = current_file_dir.parent
    # project_root_absolute = project_root.resolve()
    # static_root_absolute = project_root_absolute / "static"  # or wherever the static folder actually is.
    if get == 'data':
        if not variable or variable not in get_plottable_variables(resource_url)["y_axis"]:
            raise HTTPException(status_code=404, detail="Variable not found")
        data = get_data(resource_url, variable, resample=None)
        if not output_format:
            output_format = 'csv'
        outfile = Path(os.environ['DOWNLOAD_DIR'], 'out.csv')
        compression_opts = dict(method='zip',
                                archive_name='out.csv')
        data.to_csv(outfile, compression=compression_opts)
        # return data
        return FileResponse(path=outfile, filename='out.csv.zip')


@app.get("/ncplot/download")
async def download(*,
                 resource_string: str = Query(..., title="Input text",
                                  description="some text to write into a file that can be ten served as a static file")):
    #return os.listdir('/app')
    outfile = os.path.join(os.environ['OUTPUT_DIR'], 'some_file.txt')
    with open(outfile, 'w') as test:
        test.write(resource_string)
    return Response(content=data, media_type="application/zip")
