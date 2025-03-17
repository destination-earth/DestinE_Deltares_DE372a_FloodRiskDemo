import solara

from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.hazard.forcing.wind import WindConstant, WindCSV

units = {
    "speed": Database().site.attrs.gui.units.default_velocity_units,
    "direction": Database().site.attrs.gui.units.default_direction_units
}

@solara.component
def WindTab(FORCING_LIST, SOURCE):

    forcingValue = solara.use_reactive(None)
    forcingDirection = solara.use_reactive(None)
    forcingFile = solara.use_reactive(None)

    match SOURCE.value:
        case "CONSTANT":
            solara.InputFloat(f"Constant wind speed [{units['speed']}]", value=forcingValue)
            solara.InputFloat(f"Constant wind direction [{units['direction']}]", value=forcingDirection)

            wind = WindConstant(
                speed={
                    "value": forcingValue.value,
                    "units": units['speed']
                },
                direction={
                    "value": forcingDirection.value,
                    "units": units["direction"]
                }
            )
        case "CSV":
            solara.Markdown(f"Select timeseries file, units assumed to be [{units['speed']}, {units['direction']}]")
            solara.FileBrowser(
                directory=Database().base_path,
                can_select=True,
                on_file_open=lambda x: forcingFile.set(x)
            )
            solara.Markdown(f"Selected file: {forcingFile.value}")

            wind = WindCSV(
                path=forcingFile.value,
                units=units
            )

    def add():
        FORCING_LIST.set([*FORCING_LIST, wind])

    solara.Button("Add Forcing", on_click=add())