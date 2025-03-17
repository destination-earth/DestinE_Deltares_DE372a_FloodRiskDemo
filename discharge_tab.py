import solara

from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.hazard.interface.forcing import ShapeType
from flood_adapt.object_model.io.unit_system import UnitTypesTime
from flood_adapt.object_model.hazard.forcing.discharge import DischargeCSV, DischargeConstant, DischargeSynthetic
from flood_adapt.object_model.hazard.interface.timeseries import SyntheticTimeseriesModel

units = {
    "discharge": Database().site.attrs.gui.units.default_discharge_units,
    "time": UnitTypesTime.hours
}

@solara.component
def DischargeTab(FORCING_LIST, SOURCE):

    forcingFile = solara.use_reactive(None)
    forcingValue = solara.use_reactive(None)
    forcingShape = solara.use_reactive(None)
    forcingDuration = solara.use_reactive(None)
    forcingPeak = solara.use_reactive(None)

    match SOURCE.value:
        case "CONSTANT":
            solara.InputFloat(f"Constant discharge [{units['discharge']}]", value=forcingValue)

            dis = DischargeConstant(
                discharge={
                    "value": forcingValue.value,
                    "units": units['discharge']
                }
            )

        case "CSV":
            solara.Markdown(f"Select timeseries file, units assumed to be [{units['discharge']}]")
            solara.FileBrowser(
                directory=Database().base_path,
                can_select=True,
                on_file_open=lambda x: forcingFile.set(x)
            )
            solara.Markdown(f"Selected file: {forcingFile.value}")

            dis = DischargeCSV(
                path=forcingFile.value,
                units=units["discharge"]
            )
        case "SYNTHETIC":
            shape_types = [types.name for types in ShapeType]

            solara.Select("Forcing Shape", value=forcingShape, values=shape_types)
            solara.InputFloat("Duration [h]", value=forcingDuration)
            solara.InputFloat("Peak time [h]", value=forcingPeak)
            solara.InputFloat(f"Peak Discharge [{units['discharge']}]", value=forcingValue)

            timeseries = SyntheticTimeseriesModel(
                shape_type=forcingShape.value,
                duration={
                    "value": forcingDuration.value,
                    "units": units['time']
                },
                peak_time={
                    "value": forcingPeak.value,
                    "units": units['time']
                },
                peak_value={
                    "value": forcingValue.value,
                    "units": units['discharge']
                }
            )

            dis = DischargeSynthetic(
                timeseries=timeseries
            )
    def add():
        FORCING_LIST.set([*FORCING_LIST, dis])
    
    solara.Button("Add Forcing", on_click=add())