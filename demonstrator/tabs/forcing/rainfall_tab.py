import solara
from pathlib import Path

from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.hazard.interface.forcing import ShapeType
from flood_adapt.object_model.io.unit_system import UnitTypesTime, UnitfulTime, UnitfulIntensity, UnitfulLength
from flood_adapt.object_model.hazard.forcing.rainfall import RainfallConstant, RainfallCSV, RainfallSynthetic
from flood_adapt.object_model.hazard.interface.timeseries import SyntheticTimeseriesModel

@solara.component
def RainfallTab(FORCING_LIST, SOURCE):

    units = {
        "peak_value": Database().site.attrs.gui.units.default_intensity_units,
        "cumulative": Database().site.attrs.gui.units.default_cumulative_units,
        "time": UnitTypesTime.hours
    }

    forcingFile = solara.use_reactive(None)
    forcingShape = solara.use_reactive(None)
    forcingDuration = solara.use_reactive(None)
    forcingPeak = solara.use_reactive(None)
    forcingValueType = solara.use_reactive("peak_value")
    forcingValue = solara.use_reactive(0)

    error_message = solara.use_reactive("")

    def _add(_FORCING_LIST, _ERROR_MESSAGE):
        pass

    def _clear_forcing():
        forcingFile.set(None)
        forcingShape.set(None)
        forcingDuration.set(None)
        forcingPeak.set(None)
        forcingValueType.set("peak_value")
        forcingValue.set(0)
    
    def _val_add_forcing(_FORCING_LIST, _ERROR_MESSAGE):
        for forcing in _FORCING_LIST.value:
            if "RAINFALL" in forcing.type:
                ind = _FORCING_LIST.value.index(forcing)
                _FORCING_LIST.set([*_FORCING_LIST.value[:ind], *_FORCING_LIST.value[ind+1:]])
                _ERROR_MESSAGE.set("**WARNING**: RAINFALL forcing already in forcing list, will be overwritten")
        return _FORCING_LIST, _ERROR_MESSAGE

    match SOURCE.value:
        case "CONSTANT":
            solara.InputFloat(f"Constant Intensity [{units['peak_value'].name}]", value=forcingValue)

            def _add(FORCING_LIST, error_message):
                FORCING_LIST, error_message = _val_add_forcing(
                    _FORCING_LIST=FORCING_LIST,
                    _ERROR_MESSAGE=error_message
                )
                rain = RainfallConstant(
                    intensity=UnitfulIntensity(
                        value=forcingValue.value,
                        units=units["peak_value"]
                    )
                )

                FORCING_LIST.set([*FORCING_LIST.value, rain])

        case "CSV":
            solara.Markdown(f"Select timeseries file, units assumed to be [{units['peak_value'].name}]")
            solara.FileBrowser(
                directory=Database().base_path,
                can_select=True,
                on_file_open=lambda x: forcingFile.set(x)
            )
            solara.Markdown(f"Selected file: {forcingFile.value}")

            def _add(FORCING_LIST, error_message):
                FORCING_LIST, error_message = _val_add_forcing(
                    _FORCING_LIST=FORCING_LIST,
                    _ERROR_MESSAGE=error_message
                )
                rain = RainfallCSV(
                    path = Path(forcingFile.value),
                    units=units['peak_value'].value
                )

                FORCING_LIST.set([*FORCING_LIST.value, rain])

        case "SYNTHETIC":
            shape_types = [types.name for types in ShapeType]

            solara.Select("Forcing Shape", value=forcingShape, values=shape_types)
            solara.InputFloat(f"Duration [{units['time'].name}]", value=forcingDuration)
            solara.InputFloat(f"Peak time [{units['time'].name}]", value=forcingPeak)
            solara.ToggleButtonsSingle(value=forcingValueType, values=["peak_value","cumulative"])
            solara.InputFloat(f"Rainfall value, {forcingValueType.value} [{units[forcingValueType.value].name}]", value=forcingValue)

            def _add(FORCING_LIST, error_message):
                FORCING_LIST, error_message = _val_add_forcing(
                    _FORCING_LIST=FORCING_LIST,
                    _ERROR_MESSAGE=error_message
                )
                match forcingValueType.value:
                    case "peak_value":
                        rainfall_dict = {
                            "peak_value": UnitfulIntensity(
                                value=forcingValue.value,
                                units=units['peak_value']
                            )
                        }
                    case "cumulative":
                        rainfall_dict = {
                            "cumulatvie": UnitfulLength(
                                value=forcingValue.value,
                                units=units['cumulative']
                            )
                        }
                timeseries = SyntheticTimeseriesModel(
                    shape_type=forcingShape.value,
                    duration=UnitfulTime(
                        value=forcingDuration.value,
                        units=units['time']
                    ),
                    peak_time=UnitfulTime(
                        value=forcingPeak.value,
                        units=units['time']
                    ),
                    **rainfall_dict
                )

                rain = RainfallSynthetic(
                    timeseries=timeseries
                )
                FORCING_LIST.set([*FORCING_LIST.value, rain])

    def add():
        _add(FORCING_LIST, error_message)
        _clear_forcing()

    solara.Button("Add Forcing", on_click=add)
    if error_message.value:
        solara.Markdown(f"{error_message.value}", style={"color": "red"})

    