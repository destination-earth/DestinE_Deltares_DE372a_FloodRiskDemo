import solara
import geojson

from flood_adapt.api.measures import create_measure, save_measure
from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.interface.measures import MeasureType

def _save_measure(name, mtype, geometry, attrs, filepath):
    if geometry["type"] == "LineString":
        selection_type = "polyline"
    else:
        selection_type = "polygon"

    measure_dict = {
        "name": name,
        "selection_type": selection_type,
        "polygon_file": filepath
        **attrs
    }
    measure = create_measure(type=mtype, attrs=measure_dict)
    save_measure(measure)


@solara.component
def TabMeasures(GEOM):

    measureName = solara.use_reactive("Measure Name")
    measureType = solara.use_reactive("floodwall")
    elevation_floodwall = solara.use_reactive(0)
    discharge_pump = solara.use_reactive(0)
    volume_greeninfra = solara.use_reactive(0)
    height_greeninfra = solara.use_reactive(0)
    percarea_greeninfra = solara.use_reactive(0)
    volume_storage = solara.use_reactive(0)
    elevation_prop = solara.use_reactive(0)
    elevation_floodproof = solara.use_reactive(0)

    error_message = solara.use_reactive("")
    output_message = solara.use_reactive("")

    measure_types = [e.value for e in MeasureType]

    units = {
        "length": Database().site.attrs.gui.units.default_length_units,
        "volume": Database().site.attrs.gui.units.default_volume_units,
        "discharge": Database().site.attrs.gui.units.default_discharge_units
    }

    def _reset_measure_params():
        elevation_floodwall.set(0)
        discharge_pump.set(0)
        volume_greeninfra.set(0)
        height_greeninfra.set(0)
        percarea_greeninfra.set(0)
        volume_storage.set(0)
        elevation_prop.set(0)
        elevation_floodproof.set(0)

    with solara.Card("Measures", style={"width": "100%", "padding": "10px"}):
        solara.InputText("Measure Name", value=measureName, continuous_update=True)
        solara.Markdown(f"**Your Measure Name**: {measureName.value}")

    solara.Select(label="Measure Type", value=measureType, values=measure_types)

    match measureType.value:
        case "floodwall" | "thin_dam" | "levee":
            _reset_measure_params()
            solara.InputFloat("Elevation [m]", value=elevation_floodwall, continuous_update=True)
            measure_attr = {"elevation": {"value": elevation_floodwall.value, "units": units["length"].value}}
        case "pump" | "culvert":
            _reset_measure_params()
            solara.InputFloat("Discharge [m³/s]", value=discharge_pump, continuous_update=True)
            measure_attr = {"discharge": {"value": discharge_pump.value, "units": units["volume"].value}}
        case "water_square" | "total_storage" | "greening":
            _reset_measure_params()
            solara.InputFloat("Volume [m³]", value=volume_greeninfra, continuous_update=True)
            solara.InputFloat("Height [m]", value=height_greeninfra, continuous_update=True)
            solara.InputFloat("Percentage Area [%]", value=percarea_greeninfra, continuous_update=True)
            measure_attr = {
                "volume": {"value": volume_greeninfra.value, "units": units["volume"].value},
                "height": {"value": height_greeninfra.value, "units": units["length"].value},
                "percent_area": percarea_greeninfra.value
            }
        case "elevate_properties":
            _reset_measure_params()
            solara.InputFloat("Elevation [m]", value=elevation_prop, continuous_update=True)
            measure_attr = {"elevation": {"value": elevation_prop.value, "units": units["length"].value}}
        case "floodproof_properties":
            _reset_measure_params()
            solara.InputFloat("Elevation [m]", value=elevation_floodproof, continuous_update=True)
            measure_attr = {"elevation": {"value": elevation_floodproof.value, "units": units["length"].value}}
        case "buyout_properties":
            _reset_measure_params()
            pass

    solara.Markdown("Place the measure on the map")

    solara.Markdown(f"Selected geom: {GEOM.value}")

    def save_measure():
        output_message.set("")
        error_message.set("")

        if GEOM.value is None:
            error_message.set("**ERROR**: Please place a measure on the map")
            return
        
        filepath = Database().input_path / "measures" / measureName.value / "selection.geojson"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            geojson.dump(GEOM.value, f)

        _save_measure(
            name=measureName.value,
            mtype=measureType.value,
            geometry=GEOM.value,
            attrs=measure_attr,
            filepath=filepath
        )

        # Reset solara components
        GEOM.set(None)
        measureName.set("Measure Name")
        measureType.set("floodwall")
        _reset_measure_params()

    with solara.Row():
        solara.Button("Save Measure", on_click=save_measure, style={"margin-top": "20px", "margin-left": "-20px"})

    if error_message.value:
        solara.Markdown(error_message.value, style={"color": "red"})
    if output_message.value:
        solara.Markdown(f"**{output_message.value}**")
