import solara

from draw_utils import update_draw_tools_none, draw_tools_measure

measure_types = [
    "Floodwall",
    "Pump",
    "Water square",
    "Green infrastructure",
    "Water storage",
    "Elevate properties",
    "Floodproof properties",
    "Buyout properties"
]

measureName = solara.reactive("Measure Name")
measureType = solara.reactive("Floodwall")
elevation_floodwall = solara.reactive(0)
discharge_pump = solara.reactive(0)
volume_watersquare = solara.reactive(0)
height_watersquare = solara.reactive(0)
volume_greeninfra = solara.reactive(0)
height_greeninfra = solara.reactive(0)
percarea_greeninfra = solara.reactive(0)
volume_storage = solara.reactive(0)
elevation_prop = solara.reactive(0)
elevation_floodproof = solara.reactive(0)

selected_geometry = solara.reactive(None)
error_message = solara.reactive("")
output_message = solara.reactive("")

def _save_measure(GEOM, output_message, error_message):
    if GEOM.value is None:
        error_message.set("**ERROR**: Please place a measure on the map")
        return
    output_message.set("TODO: implement save measure")

    # Reset solara components
    GEOM.set(None)

@solara.component
def TabMeasures(m):
    update_draw_tools_none(m) 
    with solara.Card("Measures", style={"width": "100%", "padding": "10px"}):
        solara.InputText("Measure Name", value=measureName, continuous_update=True)
        solara.Markdown(f"**Your Measure Name**: {measureName.value}")

    solara.Select(label="Measure Type", value=measureType, values=measure_types)

    match measureType.value:
        case "Floodwall":
            solara.InputFloat("Elevation [m]", value=elevation_floodwall, continuous_update=True)
        case "Pump":
            solara.InputFloat("Discharge [m³/s]", value=discharge_pump, continuous_update=True)
        case "Water square":
            solara.InputFloat("Volume [m³]", value=volume_watersquare, continuous_update=True)
            solara.InputFloat("Height [m]", value=height_watersquare, continuous_update=True)
        case "Green infrastructure":
            solara.InputFloat("Volume [m³]", value=volume_greeninfra, continuous_update=True)
            solara.InputFloat("Height [m]", value=height_greeninfra, continuous_update=True)
            solara.InputFloat("Percentage of area [%]", value=percarea_greeninfra, continuous_update=True)
        case "Water storage":
            solara.InputFloat("Volume [m³]", value=volume_storage, continuous_update=True)
        case "Elevate properties":
            solara.InputFloat("Elevation [m]", value=elevation_prop, continuous_update=True)
        case "Floodproof properties":
            solara.InputFloat("Elevation [m]", value=elevation_floodproof, continuous_update=True)
        case "Buyout properties":
            pass

    solara.use_effect(lambda: draw_tools_measure(m, measureType), [measureType.value])

    solara.Markdown("Place the measure on the map")

    def save_measure():
        _save_measure(
            GEOM=selected_geometry,
            output_message=output_message,
            error_message=error_message
        )

    with solara.Row():
        solara.Button("Save Measure", on_click=save_measure, style={"margin-top": "20px", "margin-left": "-20px"})

    if error_message.value:
        solara.Markdown(error_message.value, style={"color": "red"})
    if output_message.value:
        solara.Markdown(f"**{output_message.value}**")
