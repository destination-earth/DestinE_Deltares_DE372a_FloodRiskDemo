import solara

from flood_adapt.api.events import get_events
from flood_adapt.api.projections import get_projections
from flood_adapt.api.strategies import get_strategies
from flood_adapt.api.scenarios import create_scenario, save_scenario

scenarioName = solara.reactive("Scenario Name")
selected_event = solara.reactive("")
selected_projection = solara.reactive("")
selected_strategy = solara.reactive("")

output_message = solara.reactive("")
error_message = solara.reactive("")

def _save_scenario(SCENARIO, EVENT, PROJECTION, STRATEGY, output_message, error_message):
    # Reset output message
    output_message.set("")
    error_message.set("")

    # Unpack solara elements
    name = SCENARIO.value
    event = EVENT.value
    projection = PROJECTION.value
    strategy = STRATEGY.value

    # Save scenario to database
    scen_dct = {
        "name": name,
        "event": event,
        "projection": projection,
        "strategy": strategy
    }

    try:
        scen = create_scenario(scen_dct)
        save_scenario(scen)

        output_message.set(f"Saving scenario {name}")
    except Exception as e:
        error_message.set(f"**ERROR**: {e}")

    # Reset solara elements
    SCENARIO.set("Scenario Name")
    EVENT.set("")
    PROJECTION.set("")
    STRATEGY.set("")


@solara.component
def TabScenario():

    with solara.Card("Initialise Scenario", style={"width": "100%", "padding": "10px"}):

        all_events = get_events()["name"]
        all_projections = get_projections()["name"]
        all_strategies = get_strategies()["name"]

        solara.InputText("Scenario Name", value=scenarioName, continuous_update=True)
        solara.Markdown(f"**Your Scenario Name**: {scenarioName.value}")
        with solara.Row(gap="10px"):
            solara.Select(label="Select Event", value=selected_event, values=all_events)
        with solara.Row(gap="10px"):
            solara.Select(label="Select Projection", value=selected_projection, values=all_projections)
        with solara.Row(gap="10px"):
            solara.Select(label="Select Strategy", value=selected_strategy, values=all_strategies)

        def save():
            _save_scenario(
                SCENARIO=scenarioName,
                EVENT=selected_event,
                PROJECTION=selected_projection,
                STRATEGY=selected_strategy,
                output_message=output_message,
                error_message=error_message
            )

        solara.Button("Save Scenario", on_click=lambda: save())

        if error_message.value:
            solara.Markdown(error_message.value, style={"color": "red"})
        if output_message.value:
            solara.Markdown(f"**{output_message.value}**") 