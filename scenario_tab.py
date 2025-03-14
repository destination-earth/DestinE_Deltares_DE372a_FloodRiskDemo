import solara

from draw_utils import update_draw_tools_none

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
    output_message.set(f"Saving {name}\nTODO: implement save scenario")

    # Reset solara elements
    SCENARIO.set("Scenario Name")
    EVENT.set("")
    PROJECTION.set("")
    STRATEGY.set("")


def _fetch_fa_objs():
    # events = db.events.get()
    events = ["E1", "E2"]
    # projections = db.projections.get()
    projections = ["P1", "P2"]
    # strategies = db.strategy.get()
    strategies = ["S1", "S2"]

    return events, projections, strategies


@solara.component
def TabScenario(m):
    update_draw_tools_none(m) 

    with solara.Card("Initialise Scenario", style={"width": "100%", "padding": "10px"}):

        all_events, all_projections, all_strategies = _fetch_fa_objs()

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