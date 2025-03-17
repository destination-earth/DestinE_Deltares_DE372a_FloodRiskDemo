import solara
import datetime as dt

from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.io.unit_system import UnitTypesTime
from flood_adapt.object_model.hazard.interface.events import Template
from flood_adapt.object_model.hazard.interface.forcing import ShapeType
from flood_adapt.object_model.hazard.event.event_factory import EventFactory
from flood_adapt.object_model.hazard.interface.timeseries import SyntheticTimeseriesModel

from draw_utils import update_draw_tools_none

start_date = solara.reactive(dt.date.today())
end_date = solara.reactive(dt.date.today())

eventName = solara.reactive("Event Name")
eventTab = solara.reactive("Time")
eventType = solara.reactive(None)

forcingName = solara.reactive("RAINFALL")
forcingSource = solara.reactive(None)
forcingFile = solara.reactive(None)
forcingValue = solara.reactive(0)
forcingList = solara.reactive([])

forcingShape = solara.reactive(None)
forcingDuration = solara.reactive(None)
forcingPeak = solara.reactive(None)
forcingValueType = solara.reactive("peak_value")

output_message = solara.reactive("")
error_message = solara.reactive("")

units = Database().site.attrs.gui.units

forcing_units = {
    "RAINFALL_peak_value": units.default_intensity_units,
    "RAINFALL_cumulative": units.default_cumulative_units,
    "RAINFALL_CSV": units.default_intensity_units,
    "RAINFALL_CONSTANT": units.default_intensity_units,
    "WIND_CONSTANT": units.default_velocity_units,
    "WIND_CSV": units.default_velocity_units,
    "WATERLEVEL_CSV": units.default_length_units,
    "WATERLEVEL_peak_value": units.default_length_units

}

def _clear_forcing():
    forcingFile.set(None)
    forcingValue.set(0)
    forcingValueType.set("peak_value")
    forcingShape.set(None)
    forcingDuration.set(None)
    forcingPeak.set(None)

def _clear_forcing_all():
    forcingSource.set(None)
    _clear_forcing()

def EventTimeTab():

    solara.Text("Select the Start Date:")
    solara.lab.InputDate(start_date)
    
    solara.Text("Select the End Date:")
    solara.lab.InputDate(end_date)
    
    if end_date.value < start_date.value:
        solara.Markdown("**Warning**: The end date cannot be earlier than the start date.", style={"color": "red"})

def EventDataTab(NAME, SOURCE):

    name = NAME.value
    source = SOURCE.value
    if source == "CSV":
        solara.FileBrowser(
            directory=Database().base_path,
            can_select=True, 
            on_file_open=lambda x: forcingFile.set(x))
        solara.Markdown(f"Selected file: {forcingFile.value}")
    elif source == "CONSTANT":
        solara.InputFloat(label=f"constant {name} here", value=forcingValue, continuous_update=True)
        solara.Markdown(f"Selected value: {forcingValue.value}")
    elif source == "SYNTHETIC":
        shape_types = [types.name for types in ShapeType]

        solara.Select("Forcing Shape", value=forcingShape, values=shape_types)
        solara.InputFloat("Duration [h]", value=forcingDuration)
        solara.InputFloat("Peak time [h]", value=forcingPeak)
        solara.ToggleButtonsSingle(value=forcingValueType, values=["peak_value","cumulative"])
        solara.InputFloat(f"{name} intensity ({forcingValueType.value})", value=forcingValue)

        source = SyntheticTimeseriesModel(
            shape_type=forcingShape.value,
            duration={
                "value": forcingDuration.value,
                "units": UnitTypesTime.hours
            },
            peak_time={
                "value": forcingPeak.value,
                "units": UnitTypesTime.hours
            },
            **{forcingValueType: {"value": forcingValue.type, "units": }}
        )

def EventForcingTab(etype):

    forcings = EventFactory._EVENT_TEMPLATES[etype][1].ALLOWED_FORCINGS
    forcing_names = [f.name for f in forcings]

    solara.Select(
        label="Weather type", 
        value=forcingName, 
        values=forcing_names,
        on_value=lambda x: _clear_forcing_all())

    forcing_sources = [s.name for s in forcings[forcingName.value]]
    solara.Select(
        label="Data source", 
        value=forcingSource, 
        values=forcing_sources,
        on_value=lambda x: _clear_forcing())
    EventDataTab(forcingName, forcingSource)

    

def _display_event_builder(ETYPE):

    start_date.set(dt.date.today())
    end_date.set(dt.date.today())

    etype = ETYPE.value
    if etype is None:
        solara.Markdown("**Please select an event type**")
        return
    if etype in ["Historical", "Hurricane"]:
        solara.Markdown(f"**Event type {etype} not supported**", style={"color": "red"})
        return

    with solara.Row(gap="10px", style={"justify-content": "flex-start", "width": "80%"}):
        solara.Button(label="Time", on_click=lambda: eventTab.set("Time"))
        solara.Button(label="Forcing", on_click=lambda: eventTab.set("Forcing"))

    match eventTab.value:
        case "Time":
            EventTimeTab()
        case "Forcing":
            EventForcingTab(etype)

def _save_inputs(event, start, end, output_message):
    # Reset output message
    output_message.set("")

    # Unpack solara elements
    event_name = event.value
    start_date = start.value
    end_date = end.value

    # Save event to database
    event_dict = {}
    event_dict["name"] = event_name
    event_dict["start_time"] = start_date.strftime('%Y-%m-%d %H:%M:%S')
    event_dict["end_time"] = end_date.strftime('%Y-%m-%d %H:%M:%S')
    event_dict["data_catalogues"] = ''
    event_dict["sfincs_forcing"] = {'meteo': '', 'waterlevel': ''}
    output_message.set("Event saved!")

    # Reset solara elements
    event.set("Event Name")
    start.set(dt.date.today())
    end.set(dt.date.today())


@solara.component
def TabEvent(m):
    update_draw_tools_none(m)
    
    with solara.Card("Configure the Weather Event", style={"width": "100%", "padding": "10px"}):
        solara.InputText("Event Name", value=eventName, continuous_update=True)
        solara.Markdown(f"**Your Event Name**: {eventName.value}")

        event_type_list = [e.value for e in Template]
        solara.Select(label="Select event type", value=eventType, values=event_type_list)
        _display_event_builder(eventType)
        
        def save():
            _save_inputs(
                event=eventName,
                start=start_date,
                end=end_date,
                output_message=output_message
            )

        solara.Button("Save Inputs", on_click=save)

        if output_message.value:
            solara.Markdown(f"**{output_message.value}**")