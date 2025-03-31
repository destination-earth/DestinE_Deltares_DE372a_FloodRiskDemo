import xarray as xr
import numpy as np
import matplotlib as mpl
from mapclassify import NaturalBreaks
import geopandas as gpd
from ipyleaflet import LegendControl
from ipywidgets import Output
from IPython.display import display, HTML

from flood_adapt.api.scenarios import get_scenario
from flood_adapt.dbs_classes.database import Database

def plot_floodmap(map, scenario_name):
    scenario = get_scenario(scenario_name)
    
    flood_fn = scenario.results_path / "Flooding"/ f"FloodMap_{scenario_name}.tif"
    base_fn = Database().static_path / "dem" / "dep_subgrid.tif"

    base = xr.open_dataarray(base_fn)
    flood = xr.open_dataarray(flood_fn)

    base = base.sel(band=1)
    flood = flood.sel(band=1).where(base>0)

    vmin = 0
    vmax = 2
    N = 5
    bins = [*np.linspace(vmin,vmax,N), np.inf]

    flood_grp = flood.groupby_bins(flood,bins)
    def minim(x):
        return (x-x+x.min(...))
    flood_bin = flood_grp.apply(minim).sortby([flood.x, flood.y])

    cmap = mpl.colormaps["Blues"]
    legend_keys = [f"<= {i}" for i in bins[1:-1]]
    legend_keys.append(f">{bins[-2]}")
    legend_vals = cmap(np.linspace(0,1,N))
    lgnd = {legend_keys[i]:mpl.colors.rgb2hex(legend_vals[i]) for i in range(N)}


    map.add_raster(flood_bin, vmin=vmin, vmax=vmax, nodata=np.nan, colormap=cmap)
    legend_control = LegendControl(lgnd, title="Flood Depth [m]", position="topright")
    map.add(legend_control)

def plot_damage_agg(map, scenario_name):
    scenario = get_scenario(scenario_name)

    agg_fn = scenario.impacts.impacts_path / f"Impacts_aggregated_{scenario_name}_region.gpkg"
    agg = gpd.read_file(agg_fn).to_crs(4326)

    cmap = mpl.colormaps["YlOrRd"]
    k = 5

    nb5 = NaturalBreaks(agg["TotalDamageEvent"], k=k)

    legend_keys = nb5.get_legend_classes()
    legend_values = cmap(np.linspace(0,1,len(legend_keys)))
    lgnd = {legend_keys[i]:mpl.colors.rgb2hex(legend_values[i]) for i in range(len(legend_keys))}

    legend_control = LegendControl(lgnd, title="Total Damage [EUR]", position="topright")

    map.add_data(
        agg,
        column="TotalDamageEvent",
        cmap="YlOrRd",
        scheme="NaturalBreaks",
        k=k,
        add_legend=False,
        style={
            "stroke": True,
            "color": "black",
            "weight": 1,
            "opacity": 1,
            "fillOpacity": 1,
        },
    )
    map.add(legend_control)

def plot_damage_build(map, scenario_name):
    scenario = get_scenario(scenario_name)

    build_fn = scenario.impacts.impacts_path/f"Impacts_building_footprints_{scenario_name}.gpkg"
    build = gpd.read_file(build_fn).to_crs(4326)

    cmap = mpl.colormaps["YlOrRd"]
    k = 5

    nb5 = NaturalBreaks(build["Total Damage"], k=k)

    legend_keys = nb5.get_legend_classes()
    legend_values = cmap(np.linspace(0,1,len(legend_keys)))
    lgnd = {legend_keys[i]:mpl.colors.rgb2hex(legend_values[i]) for i in range(len(legend_keys))}

    legend_control = LegendControl(lgnd, title="Total Damage [EUR]", position="topright")

    map.add_data(
        build,
        column="Total Damage",
        cmap="YlOrRd",
        scheme="NaturalBreaks",
        k=k,
        add_legend=False,
        style={
            "stroke": True,
            "color": "black",
            "weight": 1,
            "opacity": 1,
            "fillOpacity": 1
        }
    )
    map.add(legend_control)

def plot_metrics(scenario_name):
    scenario = get_scenario(scenario_name)

    metrics_fn = scenario.results_path / f"{scenario_name}_metrics.html"
    with open(metrics_fn, 'r', encoding='utf-8') as f:
        html_str = f.read()

    out = Output(layout={"border": "1px solid black", "object_fit": "scale-down"})
    out.append_display_data(HTML(html_str))
    display(out)

