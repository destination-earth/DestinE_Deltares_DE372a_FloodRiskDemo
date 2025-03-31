import solara
from pathlib import Path

from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.hazard.interface.forcing import ShapeType
from flood_adapt.object_model.io.unit_system import UnitTypesTime, UnitfulTime, UnitfulDischarge
from flood_adapt.object_model.hazard.forcing.discharge import DischargeCSV, DischargeConstant, DischargeSynthetic
from flood_adapt.object_model.hazard.interface.timeseries import SyntheticTimeseriesModel

@solara.component
def DischargeTab(FORCING_LIST, SOURCE):

    units = {
        "discharge": Database().site.attrs.gui.units.default_discharge_units,
        "time": UnitTypesTime.hours
    }

    forcingFile = solara.use_reactive(None)
    forcingValue = solara.use_reactive(None)
    forcingShape = solara.use_reactive(None)
    forcingDuration = solara.use_reactive(None)
    forcingPeak = solara.use_reactive(None)
    error_message = solara.use_reactive("")

    def _add(_FORCING_LIST, _ERROR_MESSAGE):
        pass

    def _clear_forcing():
        forcingFile.set(None)
        forcingValue.set(None)
        forcingShape.set(None)
        forcingDuration.set(None)
        forcingPeak.set(None)

    def _val_add_forcing(_FORCING_LIST, _ERROR_MESSAGE):
        for forcing in _FORCING_LIST.value:
            if "DISCHARGE" in forcing.type:
                ind = _FORCING_LIST.value.index(forcing)
                _FORCING_LIST.set([*_FORCING_LIST.value[:ind], *_FORCING_LIST.value[ind+1:]])
                _ERROR_MESSAGE.set("**WARNING**: DISCHARGE forcing already in forcing list, will be overwritten")
        return _FORCING_LIST, _ERROR_MESSAGE

    match SOURCE.value:
        case "CONSTANT":
            solara.InputFloat(f"Constant discharge [{units['discharge'].name}]", value=forcingValue)

            def _add(FORCING_LIST, error_message):
                FORCING_LIST, error_message = _val_add_forcing(
                    _FORCINC_LIST=FORCING_LIST,
                    _ERROR_MESSAGE=error_message
                )
                dis = DischargeConstant(
                    discharge=UnitfulDischarge(
                        value=forcingValue.value,
                        units=units['discharge']
                    )
                )
                FORCING_LIST.set([*FORCING_LIST.value, dis])

        case "CSV":
            solara.Markdown(f"Select timeseries file, units assumed to be [{units['discharge'].name}]")
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
                dis = DischargeCSV(
                    path=Path(forcingFile.value),
                    units=units["discharge"].value
                )
                FORCING_LIST.set([*FORCING_LIST.value, dis])

        case "SYNTHETIC":
            shape_types = [types.name for types in ShapeType]

            solara.Select("Forcing Shape", value=forcingShape, values=shape_types)
            solara.InputFloat(f"Duration [{units['time'].name}]", value=forcingDuration)
            solara.InputFloat(f"Peak time [{units['time'].name}]", value=forcingPeak)
            solara.InputFloat(f"Peak Discharge [{units['discharge'].name}]", value=forcingValue)

            def _add(FORCING_LIST, error_message):
                FORCING_LIST, error_message = _val_add_forcing(
                    _FORCING_LIST=FORCING_LIST,
                    _ERROR_MESSAGE=error_message
                )
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
                    peak_value=UnitfulDischarge(
                        value=forcingValue.value,
                        units=units['discharge']
                    )
                )

                dis = DischargeSynthetic(
                    timeseries=timeseries
                )
                FORCING_LIST.set([*FORCING_LIST.value, dis])
    
    def add():
        _add(FORCING_LIST, error_message)
        _clear_forcing()

    solara.Button("Add Forcing", on_click=add)