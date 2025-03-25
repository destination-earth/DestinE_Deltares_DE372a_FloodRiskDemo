import xarray as xr
import numpy as np
import rasterio
from localtileserver import TileClient, get_leaflet_tile_layer

from flood_adapt.api.scenarios import get_scenario
from flood_adapt.dbs_classes.database import Database

def plot_floodmap(map, scenario_name):
    scenario = get_scenario(scenario_name)
    
    flood_fn = scenario.results_path / "Flooding"/ f"FloodMap_{scenario_name}.tif"
    base_fn = Database().static_path / "dem" / "dep_subgrid.tif"

    base = xr.open_dataarray(base_fn).rio.reproject(4326)
    flood = xr.open_dataarray(flood_fn).rio.reproject(4326)

    base = base.sel(band=1)
    flood = flood.sel(band=1).where(base>0)

    mem_file = rasterio.MemoryFile()
    raster_dataset = mem_file.open(
        driver="GTiff",
        height=flood.shape[0],
        width=flood.shape[1],
        count=1,
        dtype=flood.dtype,
        crs=flood.rio.crs,
        transform=flood.rio.transform(),
        nodata=np.nan
    )
    raster_dataset.write(flood.data, 1)
    raster_dataset.close()

    client = TileClient(raster_dataset)
    t = get_leaflet_tile_layer(client)

    map.add(t)