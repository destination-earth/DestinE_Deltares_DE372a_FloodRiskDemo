import solara
from ipyleaflet import DrawControl

current_geometry_type = solara.reactive(None)
error_message = solara.reactive("")
selected_geometry = solara.reactive(None)
drawn_polylines = solara.reactive([])
drawn_polygons = solara.reactive([])
drawn_markers = solara.reactive([]) 
point_placed = solara.reactive(False)

def handle_draw(target, action, geo_json):
    print(f"Action: {action}, GeoJSON: {geo_json}") 
    if action == 'created' and 'geometry' in geo_json:
        geo_type = geo_json['geometry']['type']
        coords = geo_json['geometry']['coordinates']
        
        if current_geometry_type.value and current_geometry_type.value != geo_type:
            error_message.value = f"**Error**: You cannot draw a {geo_type} after a {current_geometry_type.value}. Please clear the previous geometry before adding a new type."
            return
        
        if geo_type == 'Polygon':
            polygon_coords = coords[0]
            selected_geometry.value = {'type': 'Polygon', 'coordinates': polygon_coords}
            drawn_polygons.value.append({'type': 'Polygon', 'coordinates': polygon_coords})
            print("Polygon coordinates updated:", selected_geometry.value)
        
        elif geo_type == 'LineString':  # Handling polylines
            selected_geometry.value = {'type': 'LineString', 'coordinates': coords}
            drawn_polylines.value.append({'type': 'LineString', 'coordinates': coords})
            print("Polyline coordinates updated:", selected_geometry.value)

        elif geo_type == 'Point':  # Handling markers
            if point_placed.value:
                error_message.value = "**Error**: Only one point can be placed. Please first save the measure before adding another one."
                return
            selected_geometry.value = {'type': 'Point', 'coordinates': coords}
            drawn_markers.value.append({'type': 'Point', 'coordinates': coords})
            point_placed.set(True)  # Set point placed flag to True
            print("Marker coordinates updated:", selected_geometry.value)

        current_geometry_type.value = geo_type  # Update the current geometry type
        error_message.value = ""

def clear_all_drawn(m):
    for control in m.controls:
        if isinstance(control, DrawControl):
            m.remove(control)
    draw_control = DrawControl(
        polyline={"shapeOptions": {"color": "blue", "weight": 4}},
        polygon={"shapeOptions": {"color": "red", "weight": 4}},
        marker={},
        rectangle={},
        circle={}
    )
    m.add_control(draw_control)

    drawn_polygons.set([])
    drawn_polylines.set([])
    drawn_markers.set([])
    point_placed.set(False)
    current_geometry_type.set(None)
    selected_geometry.set(None)

def update_draw_tools_none(m):
    for control in m.controls:
        if isinstance(control, DrawControl):
            m.remove(control)
    new_draw_control = DrawControl(polyline={},polygon={},circlemarker={})
    draw_control = new_draw_control
    draw_control.on_draw(handle_draw)
    m.add_control(draw_control)

def draw_tools_measure(m, measureType):
    for control in m.controls:
        if isinstance(control, DrawControl):
            m.remove(control)

    if measureType.value == "Floodwall":
        draw_control = DrawControl(
            polyline={"shapeOptions": {"color": "blue", "weight": 4}},
            polygon={},
            circlemarker={}
        )
    elif measureType.value == "Pump":
        draw_control = DrawControl(
            polyline={},
            polygon={},
            marker={}
        )
    else:
        draw_control = DrawControl(
            polyline={},
            polygon={"shapeOptions": {"color": "red", "weight": 4}},
            circlemarker={}
        )
    draw_control.on_draw(handle_draw)
    m.add_control(draw_control)

    drawn_polylines.set([])
    drawn_polygons.set([])
    drawn_markers.set([])
    point_placed.set(False)