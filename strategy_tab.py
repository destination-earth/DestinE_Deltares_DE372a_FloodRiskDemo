import solara

from flood_adapt.api.measures import get_measures
from flood_adapt.api.strategies import create_strategy, save_strategy

from draw_utils import update_draw_tools_none

strategyName = solara.reactive("Strategy Name")

error_message = solara.reactive("")
output_message = solara.reactive("")

def _save_strategy(STRATEGY, MEASURES, output_message, error_message):
    # Reset output message
    output_message.set("")
    error_message.set("")

    # Unpack solara elemens
    name = STRATEGY.value
    measure_list = [key for key, comp in MEASURES.items() if comp.value]

    # Save strategy to database
    strat_dct = {
        "name": name,
        "measures": measure_list,
        }
    
    try:
        strat = create_strategy(strat_dct)
        save_strategy(strat)

        msg = f"Saving measures {measure_list} to strategy {name}"
        output_message.set(f"{msg}")
    except Exception as e:
        error_message.set(f"**ERROR**: {e}")
    

    # Reset solara components
    STRATEGY.set("Strategy Name")
    for _, comp in MEASURES.items():
        comp.set(False)




@solara.component
def TabStrategy(m): 
    update_draw_tools_none(m) 
    with solara.Card("Strategy Name", style={"width": "100%", "padding": "10px"}):
        solara.InputText("Strategy Name", value=strategyName, continuous_update=True)
        
        measure_list = get_measures()["name"]
        measure_comps = {k: solara.use_reactive(False) for k in measure_list}

        for key, value in measure_comps.items():
            solara.Checkbox(label=key, value=value)


        def save_strategy():
            _save_strategy(
                STRATEGY=strategyName,
                MEASURES=measure_comps,
                output_message=output_message,
                error_message=error_message
            )


        with solara.Row():
            solara.Button("Save Strategy", on_click=save_strategy, style={"margin-top": "80px", "margin-left": "54px"})

        if error_message.value:
            solara.Markdown(error_message.value, style={"color": "red"})
        if output_message.value:
            solara.Markdown(f"**{output_message.value}**")