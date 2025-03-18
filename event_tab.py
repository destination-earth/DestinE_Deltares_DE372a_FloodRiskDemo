import solara
import datetime as dt

from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.hazard.interface.events import Template
from flood_adapt.object_model.hazard.event.event_factory import EventFactory

from discharge_tab import DischargeTab
from rainfall_tab import RainfallTab
from waterlevel_tab import WaterlevelTab
from wind_tab import WindTab
from draw_utils import update_draw_tools_none

start_date = solara.reactive(dt.date.today())
end_date = solara.reactive(dt.date.today())

output_message = solara.reactive("")
error_message = solara.reactive("")

def EventTimeTab():

    solara.Text("Select the Start Date:")
    solara.lab.InputDate(start_date)
    
    solara.Text("Select the End Date:")
    solara.lab.InputDate(end_date)
    
    if end_date.value < start_date.value:
        solara.Markdown("**Warning**: The end date cannot be earlier than the start date.", style={"color": "red"})


def EventForcingTab(etype,FORCING_NAME, FORCING_SOURCE, FORCING_LIST):

    forcings = EventFactory._EVENT_TEMPLATES[etype][1].ALLOWED_FORCINGS
    forcing_names = [f.name for f in forcings]

    solara.Select(
        label="Weather type", 
        value=FORCING_NAME, 
        values=forcing_names,
        on_value=lambda x: FORCING_SOURCE.set(None))

    forcing_sources = [s.name for s in forcings[FORCING_NAME.value]]
    solara.Select(
        label="Data source", 
        value=FORCING_SOURCE, 
        values=forcing_sources,
        # on_value=lambda x: _clear_forcing(),
        )

    match FORCING_NAME.value:
        case "DISCHARGE":
            if Database().site.attrs.sfincs.river:
                DischargeTab(FORCING_LIST, FORCING_SOURCE)
            else:
                solara.Markdown("**SFINCS model does not contain rivers**")
        case "RAINFALL":
            RainfallTab(FORCING_LIST, FORCING_SOURCE)
        case "WATERLEVEL":
            WaterlevelTab(FORCING_LIST, FORCING_SOURCE)
        case "WIND":
            WindTab(FORCING_LIST, FORCING_SOURCE)
    

def _display_event_builder(EVENT_TYPE, EVENT_TAB, FORCING_NAME, FORCING_SOURCE, FORCING_LIST):

    start_date.set(dt.date.today())
    end_date.set(dt.date.today())

    etype = EVENT_TYPE.value
    if etype is None:
        solara.Markdown("**Please select an event type**")
        return
    if etype in ["Historical", "Hurricane"]:
        solara.Markdown(f"**Event type {etype} not supported**", style={"color": "red"})
        return

    with solara.Row(gap="10px", style={"justify-content": "flex-start", "width": "80%"}):
        solara.Button(label="Time", on_click=lambda: EVENT_TAB.set("Time"))
        solara.Button(label="Forcing", on_click=lambda: EVENT_TAB.set("Forcing"))

    match EVENT_TAB.value:
        case "Time":
            EventTimeTab()
        case "Forcing":
            EventForcingTab(etype,FORCING_NAME, FORCING_SOURCE, FORCING_LIST)

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

    eventName = solara.use_reactive("Event Name")
    eventTab = solara.use_reactive("Time")
    eventType = solara.use_reactive(None)

    forcingName = solara.use_reactive("RAINFALL")
    forcingSource = solara.use_reactive(None)
    forcingList = solara.use_reactive([])

    update_draw_tools_none(m)
    
    with solara.Card("Configure the Weather Event", style={"width": "100%", "padding": "10px"}):
        solara.InputText("Event Name", value=eventName, continuous_update=True)
        solara.Markdown(f"**Your Event Name**: {eventName.value}")

        event_type_list = [e.value for e in Template]
        solara.Select(label="Select event type", value=eventType, values=event_type_list)
        _display_event_builder(
            eventType,
            eventTab,
            forcingName,
            forcingSource,
            forcingList
            )
        
        def save():
            _save_inputs(
                event=eventName,
                start=start_date,
                end=end_date,
                output_message=output_message
            )

        solara.Button("Save Inputs", on_click=save)

        solara.Markdown(f"**Forcings stored**: {forcingList.value}")

        if output_message.value:
            solara.Markdown(f"**{output_message.value}**")