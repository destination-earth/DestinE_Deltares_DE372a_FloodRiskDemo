import solara

from flood_adapt.api.scenarios import get_scenarios
from flood_adapt.dbs_classes.database import Database

def _run_scenario(SCENARIO, output_message, error_message):
    if SCENARIO.value is None:
        error_message.set("**ERROR**: No scenario selected")
        return
    
    scenario = SCENARIO.value
    output_message.set(f"Running scenario {scenario}")
    try:
        Database().run_scenario(scenario_name=scenario)
        output_message.set(f"Scenario {scenario} finished!")
    except Exception as e:
        error_message.set(f"**ERROR**: {e}")



@solara.component
def TabRun():

    selected_scenario = solara.use_reactive(None)
    output_message = solara.use_reactive(None)
    error_message = solara.use_reactive(None)

    with solara.Card("Save inputs and Run model", style={"width": "100%", "padding": "10px"}):

        all_scenarios = get_scenarios()["name"]

        solara.Markdown("**Run Scenario:**")
        solara.Select(label="Select Scenario", value=selected_scenario, values=all_scenarios)

        def run():
            _run_scenario(
                SCENARIO=selected_scenario,
                output_message=output_message,
                error_message=error_message
            )

        solara.Button("Run", on_click=run)

        if output_message.value:
            solara.Markdown(f"**{output_message}**") 
        if error_message.value:
            solara.Markdown(f"{error_message.value}", style={"color", "red"})