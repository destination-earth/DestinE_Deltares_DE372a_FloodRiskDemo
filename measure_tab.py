import solara
import geojson

from flood_adapt.api.measures import create_measure, save_measure
from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.interface.measures import MeasureType
from flood_adapt.object_model.io.unit_system import UnitfulLength, UnitfulDischarge, UnitfulVolume

def _save_measure(name, mtype, geometry, attrs, filepath):
    if geometry["type"] == "LineString":
        selection_type = "polyline"
    else:
        selection_type = "polygon"

    measure_dict = {
        "name": name,
        "selection_type": selection_type,
        "polygon_file": filepath,
        **attrs
    }

    measure = create_measure(type=mtype, attrs=measure_dict)
    save_measure(measure)
        
@solara.component
def _floodwallTab(MATTRS, units):
    measureValue = solara.use_reactive(0)
    solara.InputFloat(label="Elevation [m]", value=measureValue, continuous_update=True)
    measure_dict = {
        "elevation": UnitfulLength(
            value=measureValue.value,
            units=units['length']
        )
    }
    MATTRS.set(measure_dict)

@solara.component
def _pumpTab(MATTRS, units):
    measureValue = solara.use_reactive(0)
    solara.InputFloat(label="Discharge [m³/s]", value=measureValue, continuous_update=True)
    measure_dict = {
        "discharge": UnitfulDischarge(
            value=measureValue.value,
            units=units['discharge']
        )
    }
    MATTRS.set(measure_dict)

@solara.component
def _storageTab(MATTRS, units):
    measureValue1 = solara.use_reactive(0)
    measureValue2 = solara.use_reactive(0)
    measureValue3 = solara.use_reactive(0)

    solara.InputFloat("Volume [m³]", value=measureValue1, continuous_update=True)
    solara.InputFloat("Height [m]", value=measureValue2, continuous_update=True)
    solara.InputFloat("Percentage Area [%]", value=measureValue3, continuous_update=True)

    measure_dict = {
        "volume": UnitfulVolume(
            value=measureValue1.value,
            units=units["volume"]
        ),
        "height": UnitfulLength(
            value=measureValue2.value,
            units=units["length"]
        ),
        "percent_area": measureValue3.value
    }

    MATTRS.set(measure_dict)

@solara.component
def _buyoutTab(MATTRS, units):
    pass

@solara.component
def TabMeasures(GEOM):

    measureName = solara.use_reactive("Measure Name")
    measureType = solara.use_reactive(None)
    measureAttrs = solara.use_reactive({})

    error_message = solara.use_reactive("")
    output_message = solara.use_reactive("")

    measure_types = [e.value for e in MeasureType]

    units = {
        "length": Database().site.attrs.gui.units.default_length_units,
        "volume": Database().site.attrs.gui.units.default_volume_units,
        "discharge": Database().site.attrs.gui.units.default_discharge_units
    }

    with solara.Card("Measures", style={"width": "100%", "padding": "10px"}):
        solara.InputText("Measure Name", value=measureName, continuous_update=True)
        solara.Markdown(f"**Your Measure Name**: {measureName.value}")

        solara.Select(label="Measure Type", value=measureType, values=measure_types)

        match measureType.value:
            case "floodwall":
                _floodwallTab(MATTRS=measureAttrs, units=units)
            case "thin_dam":
                _floodwallTab(MATTRS=measureAttrs, units=units)
            case "levee":
                _floodwallTab(MATTRS=measureAttrs, units=units)
            case "pump" | "culvert":
                _pumpTab(MATTRS=measureAttrs, units=units)
            case "water_square" | "total_storage" | "greening":
                _storageTab(MATTRS=measureAttrs, units=units)
            case "elevate_properties" | "floodproof_properties":
                _floodwallTab(MATTRS=measureAttrs, units=units)
            case "buyout_properties":
                _buyoutTab(MATTRS=measureAttrs, units=units)

        solara.Markdown("Place the measure on the map")

        solara.Markdown(f"Selected geom: {GEOM.value}")
        solara.Markdown(f"Measure attrs: {measureAttrs.value}")

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
            try:
                output_message.set("Saving measure")
                _save_measure(
                    name=measureName.value,
                    mtype=measureType.value,
                    geometry=GEOM.value,
                    attrs=measureAttrs.value,
                    filepath=filepath.as_posix(),
                )
            except Exception as e:
                error_message.set(f"**ERROR**: {e}")

            # Reset solara components
            GEOM.set(None)
            measureName.set("Measure Name")
            measureType.set(None)
            measureAttrs.set({})

        with solara.Row():
            solara.Button("Save Measure", on_click=save_measure, style={"margin-top": "20px", "margin-left": "-20px"})

        if error_message.value:
            solara.Markdown(error_message.value, style={"color": "red"})
        if output_message.value:
            solara.Markdown(f"**{output_message.value}**")
