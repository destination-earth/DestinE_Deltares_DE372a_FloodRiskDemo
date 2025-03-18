import solara
from pathlib import Path

from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.io.unit_system import UnitfulDirection, UnitfulVelocity
from flood_adapt.object_model.hazard.forcing.wind import WindConstant, WindCSV

@solara.component
def WindTab(FORCING_LIST, SOURCE):

    units = {
        "speed": Database().site.attrs.gui.units.default_velocity_units,
        "direction": Database().site.attrs.gui.units.default_direction_units
    }

    forcingValue = solara.use_reactive(None)
    forcingDirection = solara.use_reactive(None)
    forcingFile = solara.use_reactive(None)
    error_message = solara.use_reactive("")

    def _add(_FORCING_LIST, _ERROR_MESSAGE):
        pass
    
    def _clear_forcing():
        forcingValue.set(None)
        forcingDirection.set(None)
        forcingFile.set(None)


    def _val_add_forcing(_FORCING_LIST, _ERROR_MESSAGE):
        for forcing in _FORCING_LIST.value:
            if "WIND" in forcing.type:
                ind = _FORCING_LIST.value.index(forcing)
                _FORCING_LIST.set([*_FORCING_LIST.value[:ind], *_FORCING_LIST.value[ind+1:]])
                _ERROR_MESSAGE.set("**WARNING**: WIND forcing already in forcing list, will be overwritten")
        return _FORCING_LIST, _ERROR_MESSAGE


    match SOURCE.value:
        case "CONSTANT":
            solara.InputFloat(f"Constant wind speed [{units['speed'].name}]", value=forcingValue)
            solara.InputFloat(f"Constant wind direction [{units['direction'].name}]", value=forcingDirection)

            def _add(FORCING_LIST, error_message):
                FORCING_LIST, error_message = _val_add_forcing(
                    _FORCING_LIST=FORCING_LIST, 
                    _ERROR_MESSAGE=error_message,
                    )
                wind = WindConstant(
                    speed=UnitfulVelocity(
                        value=forcingValue.value,
                        units=units["speed"]
                    ),
                    direction=UnitfulDirection(
                        value=forcingDirection.value,
                        units=units["direction"]
                    )
                )
                FORCING_LIST.set([*FORCING_LIST.value, wind])

        case "CSV":
            solara.Markdown(f"Select timeseries file, units assumed to be [{units['speed'].name}, {units['direction'].name}]")
            solara.FileBrowser(
                directory=Database().base_path,
                can_select=True,
                on_file_open=lambda x: forcingFile.set(x)
            )
            solara.Markdown(f"Selected file: {forcingFile.value}")

            def _add(FORCING_LIST, error_message):
                FORCING_LIST, error_message = _val_add_forcing(_FORCING_LIST=FORCING_LIST, _ERROR_MESSAGE=error_message)
                wind = WindCSV(
                    path=Path(forcingFile.value),
                    units=units
                )
                FORCING_LIST.set([*FORCING_LIST.value, wind])

    def add():
        _add(FORCING_LIST, error_message)
        _clear_forcing()

    solara.Button("Add Forcing", on_click=add)
    if error_message.value:
        solara.Markdown(f"{error_message.value}", style={"color": "red"})