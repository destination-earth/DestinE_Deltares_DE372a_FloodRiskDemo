import solara
from pathlib import Path

from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.io.unit_system import UnitTypesTime, UnitfulLength, UnitfulTime
from flood_adapt.object_model.hazard.interface.forcing import ShapeType
from flood_adapt.object_model.hazard.forcing.waterlevels import WaterlevelCSV, WaterlevelSynthetic, TideModel, SurgeModel
from flood_adapt.object_model.hazard.interface.timeseries import SyntheticTimeseriesModel

@solara.component
def WaterlevelTab(FORCING_LIST, SOURCE):

    units = {
        "waterlevel": Database().site.attrs.gui.units.default_length_units,
        "phase": UnitTypesTime.seconds,
        "time": UnitTypesTime.hours,
    }

    forcingFile = solara.use_reactive(None)
    forcingHarmAmp = solara.use_reactive(0)
    forcingHarmPhase = solara.use_reactive(0)

    forcingShape = solara.use_reactive(None)
    forcingDuration = solara.use_reactive(None)
    forcingPeak = solara.use_reactive(None)
    forcingValue = solara.use_reactive(0)

    error_message = solara.use_reactive("")

    def _add(_FORCING_LIST, _ERROR_MESSAGE):
        pass

    def _clear_forcing():
        forcingFile.set(None)
        forcingHarmAmp.set(0)
        forcingHarmPhase.set(0)
        forcingShape.set(None)
        forcingDuration.set(None)
        forcingPeak.set(None)
        forcingValue.set(0)

    def _val_add_forcing(_FORCING_LIST, _ERROR_MESSAGE):
        for forcing in _FORCING_LIST.value:
            if "WATERLEVEL" in forcing.type:
                ind = _FORCING_LIST.value.index(forcing)
                _FORCING_LIST.set([*_FORCING_LIST.value[:ind], *_FORCING_LIST.value[ind+1:]])
                _ERROR_MESSAGE.set("**WARNING**: WATERLEVEL forcing already in forcing list, will be overwritten")
        return _FORCING_LIST, _ERROR_MESSAGE

    match SOURCE.value:
        case "CSV":
            solara.Markdown(f"Select timeseries file, units assumed to be [{units['waterlevel'].name}]")
            solara.FileBrowser(
                directory=Database().base_path,
                can_select=True,
                on_file_open=lambda x: forcingFile.set(x)
            )
            solara.Markdown(f"Selected file: {forcingFile.value}")

            def _add(FORCING_LIST, error_message):
                FORCING_LIST, error_message = _val_add_forcing(
                    _FORCING_LIST=FORCING_LIST,
                    _ERROR_MESSAGE=error_message,
                    )
                waterlevel = WaterlevelCSV(
                    path=Path(forcingFile.value),
                    units=units['waterlevel'].value
                )
                FORCING_LIST.set([*FORCING_LIST.value, waterlevel])

        case "SYNTHETIC":
            with solara.Card("Tide Component"):
                solara.InputFloat(f"Harmonic Amplitude [{units['waterlevel'].name}]", value=forcingHarmAmp)
                solara.InputFloat(f"Harmonic Phase [{units['phase'].name}]", value=forcingHarmPhase)
                solara.Markdown("Harmonic Period fixed to 12.4h")
            with solara.Card("Surge Component"):
                shape_types = [types.name for types in ShapeType]

                solara.Select("Forcing Shape", value=forcingShape, values=shape_types)
                solara.InputFloat(f"Duration [{units['time'].name}]", value=forcingDuration)
                solara.InputFloat(f"Peak time [{units['time'].name}]", value=forcingPeak)
                solara.InputFloat(f"Peak Surge [{units['waterlevel'].name}]", value=forcingValue)

                def _add(FORCING_LIST, error_message):
                    FORCING_LIST, error_message = _val_add_forcing(
                        _FORCING_LIST=FORCING_LIST,
                        _ERROR_MESSAGE=error_message,
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
                        peak_value=UnitfulLength(
                            value=forcingValue.value,
                            units=units['waterlevel']
                        ),
                    )

                    waterlevel = WaterlevelSynthetic(
                        tide=TideModel(
                            harmonic_amplitude=UnitfulLength(
                                value=forcingHarmAmp.value,
                                units=units['waterlevel']
                            ),
                            harmonic_phase=UnitfulTime(
                                value=forcingHarmPhase.value,
                                units=units['phase']
                            ),
                        ),
                        surge=SurgeModel(
                            timeseries=timeseries
                        )
                    )
                    FORCING_LIST.set([*FORCING_LIST.value, waterlevel])

    def add():
        _add(FORCING_LIST, error_message)
        _clear_forcing()

    solara.Button("Add Forcing", on_click=add)
    if error_message.value:
        solara.Markdown(f"{error_message.value}", style={"color": "red"})

