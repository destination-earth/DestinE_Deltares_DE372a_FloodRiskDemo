import solara

from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.io.unit_system import UnitTypesTime
from flood_adapt.object_model.hazard.interface.forcing import ShapeType
from flood_adapt.object_model.hazard.forcing.waterlevels import WaterlevelCSV, WaterlevelSynthetic, TideModel, SurgeModel
from flood_adapt.object_model.hazard.interface.timeseries import SyntheticTimeseriesModel

units = {
    "waterlevel": Database().site.attrs.gui.units.default_length_units,
    "phase": UnitTypesTime.seconds,
    "time": UnitTypesTime.hours,
}
@solara.component
def WaterlevelTab(FORCING_LIST, SOURCE):

    forcingFile = solara.use_reactive(None)
    forcingHarmAmp = solara.use_reactive(0)
    forcingHarmPhase = solara.use_reactive(0)

    forcingShape = solara.use_reactive(None)
    forcingDuration = solara.use_reactive(None)
    forcingPeak = solara.use_reactive(None)
    forcingValue = solara.use_reactive(0)


    match SOURCE.value:
        case "CSV":
            solara.Markdown(f"Select timeseries file, units assumed to be [{units['waterlevel']}]")
            solara.FileBrowser(
                directory=Database().base_path,
                can_select=True,
                on_file_open=lambda x: forcingFile.set(x)
            )
            solara.Markdown(f"Selected file: {forcingFile.value}")

            waterlevel = WaterlevelCSV(
                path=forcingFile.value,
                units=units['waterlevel']
            )
        case "SYNTHETIC":
            with solara.Card("Tide Component"):
                solara.InputFloat(f"Harmonic Amplitude [{units['waterlevel']}]", value=forcingHarmAmp)
                solara.InputFloat(f"Harmonic Phase [{units['phase']}]", value=forcingHarmPhase)
                solara.Markdown("Harmonic Period fixed to 12.4h")
            with solara.Card("Surge Component"):
                shape_types = [types.name for types in ShapeType]

                solara.Select("Forcing Shape", value=forcingShape, values=shape_types)
                solara.InputFloat(f"Duration [{units['time']}]", value=forcingDuration)
                solara.InputFloat(f"Peak time [{units['time']}]", value=forcingPeak)
                solara.InputFloat(f"Peak Surge [{units['waterlevel']}]", value=forcingValue)

                timeseries = SyntheticTimeseriesModel(
                    shape_type=forcingShape.value,
                    duration={
                        "value": forcingDuration.value,
                        "units": UnitTypesTime.hours
                    },
                    peak_time={
                        "value": forcingPeak,
                        "units": UnitTypesTime.hours,
                    },
                    peak_value={
                        "value": forcingValue.value,
                        "units": units['waterlevel']
                    }
                )

                waterlevel = WaterlevelSynthetic(
                    tide=TideModel(
                        harmonic_amplitude={
                            "value": forcingHarmAmp.value,
                            "units": units['waterlevel']
                        },
                        harmonic_phase={
                            "value": forcingHarmPhase.value,
                            "units": units['phase']
                        },
                    ),
                    surge=SurgeModel(
                        timeseries=timeseries
                    )
                )

    def add():
        FORCING_LIST.set([*FORCING_LIST, waterlevel])

    solara.Button("Add Forcing", on_click=add())

