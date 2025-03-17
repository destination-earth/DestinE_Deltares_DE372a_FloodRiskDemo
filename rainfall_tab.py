import solara

from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.hazard.interface.forcing import ShapeType
from flood_adapt.object_model.io.unit_system import UnitTypesTime
from flood_adapt.object_model.hazard.forcing.rainfall import RainfallConstant, RainfallCSV, RainfallSynthetic
from flood_adapt.object_model.hazard.interface.timeseries import SyntheticTimeseriesModel

units = {
    "peak_value": Database().site.attrs.gui.units.default_intensity_units,
    "cumulative": Database().site.attrs.gui.units.default_cumulative_units,
    "time": UnitTypesTime.hours
}

@solara.component
def RainfallTab(FORCING_LIST, SOURCE):

    forcingFile = solara.use_reactive(None)
    forcingShape = solara.use_reactive(None)
    forcingDuration = solara.use_reactive(None)
    forcingPeak = solara.use_reactive(None)
    forcingValueType = solara.use_reactive("peak_value")
    forcingValue = solara.use_reactive(0)
    
    match SOURCE.value:
        case "CONSTANT":
            solara.InputFloat(f"Constant Intensity [{units['peak_value']}]", value=forcingValue)

            rain = RainfallConstant(
                intensity={
                    "value": forcingValue.value,
                    "units": units['peak_value']
                }
            )

        case "CSV":
            solara.Markdown(f"Select timeseries file, units assumed to be [{units['peak_value']}]")
            solara.FileBrowser(
                directory=Database().base_path,
                can_select=True,
                on_file_open=lambda x: forcingFile.set(x)
            )
            solara.Markdown(f"Selected file: {forcingFile.value}")

            rain = RainfallCSV(
                path = forcingFile.value,
                units=units['peak_value']
            )
        case "SYNTHETIC":
            shape_types = [types.name for types in ShapeType]

            solara.Select("Forcing Shape", value=forcingShape, values=shape_types)
            solara.InputFloat(f"Duration [{units['time']}]", value=forcingDuration)
            solara.InputFloat(f"Peak time [{units['time']}]", value=forcingPeak)
            solara.ToggleButtonsSingle(value=forcingValueType, values=["peak_value","cumulative"])
            solara.InputFloat(f"Rainfall value, {forcingValueType.value} [{units[forcingValueType.value]}]", value=forcingValue)

            timeseries = SyntheticTimeseriesModel(
                shape_type=forcingShape.value,
                duration={
                    "value": forcingDuration.value,
                    "units": units['time']
                },
                peak_time={
                    "value": forcingPeak,
                    "units": units['time']
                },
                **{forcingValueType:{
                    "value": forcingValue.value,
                    "units": units[forcingValueType.value]
                }}
            )

            rain = RainfallSynthetic(
                timeseries=timeseries
            )

    def add():
        FORCING_LIST.set([*FORCING_LIST.value, rain])


    solara.Button("Add Forcing", on_click=add())

    