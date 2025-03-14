import solara

from draw_utils import update_draw_tools_none

selected_scenario = solara.reactive("")
output_message = solara.reactive("")
error_message = solara.reactive("")

def _fetch_fa_scenarios():
    # scenarios = db.scenarios.get()
    scenarios = ["mock"]

    return scenarios

def _run_scenario(scenario, output_message, error_message):
    if scenario.value is None:
        error_message.set("**ERROR**: No scenario selected")
        return
    output_message.set(f"Running scenario {scenario.value}")

@solara.component
def TabRun(m):
    update_draw_tools_none(m) 

    with solara.Card("Save inputs and Run model", style={"width": "100%", "padding": "10px"}):

        all_scenarios = _fetch_fa_scenarios()

        solara.Markdown("**Run Scenario:**")
        solara.Select(label="Select Scenario", value=selected_scenario, values=all_scenarios)

        def run():
            _run_scenario(
                scenario=selected_scenario,
                output_message=output_message,
                error_message=error_message
            )

        solara.Button("Run", on_click=lambda: run())

        if output_message.value:
            solara.Markdown(f"**{output_message}**") 