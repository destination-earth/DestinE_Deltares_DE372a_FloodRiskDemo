import solara
import datetime as dt

from flood_adapt.api.events import create_event, save_event
from flood_adapt.dbs_classes.database import Database
from flood_adapt.object_model.hazard.interface.events import Template
from flood_adapt.object_model.hazard.event.event_factory import EventFactory

from discharge_tab import DischargeTab
from rainfall_tab import RainfallTab
from waterlevel_tab import WaterlevelTab
from wind_tab import WindTab

start_date = solara.reactive(dt.date.today())
start_time = solara.reactive(dt.time(0,0,0))
end_date = solara.reactive(dt.date.today())
end_time = solara.reactive(dt.time(0,0,0))

output_message = solara.reactive("")
error_message = solara.reactive("")

def EventTimeTab():

    solara.Text("Select the Start Date:")
    solara.lab.InputDate(start_date)
    solara.Text("Select Start Time")
    solara.lab.InputTime(start_time)

    solara.Text("Select the End Date:")
    solara.lab.InputDate(end_date)
    solara.Text("Select End Time")
    solara.lab.InputTime(end_time)
    
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
        )

    match FORCING_NAME.value:
        case "DISCHARGE":
            if Database().site.attrs.sfincs.river:
                DischargeTab(FORCING_LIST, FORCING_SOURCE)
            else:
                solara.Markdown("**SFINCS model does not contain rivers**", style={"color": "red"})
        case "RAINFALL":
            RainfallTab(FORCING_LIST, FORCING_SOURCE)
        case "WATERLEVEL":
            WaterlevelTab(FORCING_LIST, FORCING_SOURCE)
        case "WIND":
            WindTab(FORCING_LIST, FORCING_SOURCE)
    

def _display_event_builder(EVENT_TYPE, EVENT_TAB, FORCING_NAME, FORCING_SOURCE, FORCING_LIST):

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

def _parse_forcing_list(forcing_list):
    forcing_dict = {}
    for forcing in forcing_list:
        forcing_dict.update(
            {forcing.type.value: [forcing]}
        )
    return forcing_dict

def _save_inputs(EVENT, ETYPE, start, end, FORCINGS, output_message, error_message):
    # Reset output message
    output_message.set("")
    error_message.set("")

    # Unpack solara elements
    event_name = EVENT.value
    etype = ETYPE.value
    forcings = FORCINGS.value

    # Save event to database
    event_dict = {
        "name": event_name,
        "time": {
            "start_time": start,
            "end_time": end
        },
        "template": etype,
        "mode": "single_event",
        "forcings": _parse_forcing_list(forcings)
    }

    try:
        event = create_event(event_dict)
        save_event(event)

        output_message.set(f"Saving Event {event_name}")
    except Exception as e:
        error_message.set(f"**ERROR**: {e}")

    # Reset solara elements
    EVENT.set("Event Name")
    ETYPE.set(None)
    FORCINGS.set([])


@solara.component
def TabEvent():

    eventName = solara.use_reactive("Event Name")
    eventTab = solara.use_reactive("Time")
    eventType = solara.use_reactive(None)

    forcingName = solara.use_reactive("RAINFALL")
    forcingSource = solara.use_reactive(None)
    forcingList = solara.use_reactive([])
    
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
        
        start = dt.datetime.combine(start_date.value, start_time.value)
        end = dt.datetime.combine(end_date.value, end_time.value)

        def save():
            _save_inputs(
                EVENT=eventName,
                ETYPE=eventType,
                start=start,
                end=end,
                FORCINGS=forcingList,
                output_message=output_message,
                error_message=error_message
            )
            start_date.set(dt.date.today())
            start_time.set(dt.time(0,0,0))
            end_date.set(dt.time.today())
            end_time.set(dt.time(0,0,0))


        solara.Markdown(f"**Forcings stored**: {forcingList.value}")
        solara.Markdown(f"**Time stored**: start {start}, end {end}")
        if output_message.value:
            solara.Markdown(f"**{output_message.value}**")
        if error_message.value:
            solara.Markdown(f"{error_message.value}", style={'color': 'red'})

        solara.Button("Save Inputs", on_click=save)

        