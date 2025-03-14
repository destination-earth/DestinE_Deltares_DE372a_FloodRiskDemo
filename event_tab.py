import solara

import datetime as dt

from draw_utils import update_draw_tools_none

start_date = solara.reactive(dt.date.today())
end_date = solara.reactive(dt.date.today())
eventName = solara.reactive("Event Name")
output_message = solara.reactive("")

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

        solara.Text("Select the Start Date:")
        solara.lab.InputDate(start_date)
        
        solara.Text("Select the End Date:")
        solara.lab.InputDate(end_date)
        
        if end_date.value < start_date.value:
            solara.Markdown("**Warning**: The end date cannot be earlier than the start date.", style={"color": "red"})
        
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