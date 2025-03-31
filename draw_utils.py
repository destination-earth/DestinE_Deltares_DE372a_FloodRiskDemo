import leafmap.leafmap as leafmap
from ipyleaflet import GeomanDrawControl, basemaps, DrawControl, WidgetControl

def draw_map(center):
    m = leafmap.Map(center=center, zoom=13, scroll_wheel_zoom=True, basemap=basemaps.OpenStreetMap.Mapnik)
    for control in m.controls:
        if isinstance(control, DrawControl) or isinstance(control, WidgetControl):
            m.remove(control)
    return m

def draw_map_controls(center):
    m = leafmap.Map(center=center, zoom=13, scroll_wheel_zoom=True, basemap=basemaps.OpenStreetMap.Mapnik)
    for control in m.controls:
        if isinstance(control, DrawControl) or isinstance(control, WidgetControl):
            m.remove(control)
    draw_control = GeomanDrawControl()
    m.add_control(draw_control)
    
    return m

def update_draw_tools_none(m):
    for control in m.controls:
        if isinstance(control,GeomanDrawControl):
            m.remove(control)
    
def draw_tools_measure(m, MTYPE):
    for control in m.controls:
        if isinstance(control,GeomanDrawControl):
            m.remove(control)
    draw_control = GeomanDrawControl()
    match MTYPE.value:
        case "Floodwall":
            draw_control.polyline = {
                "shapeoptions": {
                    "color": "blue",
                    "weigth": 4
                }
            }
        case "Pump":
            pass
        case _:
            draw_control.polygon = {
                "shapeOptions": {
                    "color": "red",
                    "weight": 4
                }
            }
    m.add(draw_control)

def _handle_draw(target, action, geo_json, GEOM):
    if action == 'remove':
        GEOM.set(None)
        target.clear()
    else:
        # geo_json will be a singleton list containing the dict
        geometry = geo_json[0]["geometry"]
        GEOM.set(geometry)
