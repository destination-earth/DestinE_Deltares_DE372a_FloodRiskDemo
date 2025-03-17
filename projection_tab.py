import solara

from flood_adapt.dbs_classes.database import Database
from flood_adapt.api.projections import create_projection, save_projection

from draw_utils import update_draw_tools_none

SLR_input = solara.reactive(0.0)
RAIN_input = solara.reactive(0.0)
POP_input = solara.reactive(0.0)
ECON_input = solara.reactive(0.0)
projName = solara.reactive("Projection Name")
output_message = solara.reactive("")
error_message = solara.reactive("")

def _save_inputs_projections(name, SLR, RAIN, POP, ECON, output_message, error_message):
        # Reset output message
        output_message.set("")

        # Unpack solara elements
        units = Database().site.attrs.gui.units
        proj_name = name.value
        slr = {
             "value": SLR.value,
             "units": units.default_length_units
        }
        rain = RAIN.value
        pop = POP.value
        econ = ECON.value

        # Save projection to database
        proj_dict = {}
        proj_dict["name"] = proj_name
        proj_dict["physical_projection"] = {'sea_level_rise': slr,
                                            'rainfall_increase': rain}
        proj_dict["socio_economic_change"] = {'population_growth_existing': pop,
                                            'economic_growth': econ}
        
        try:
            proj =  create_projection(attrs=proj_dict)
            save_projection(projection=proj)

            output_message.set(f"Projection {proj_name} saved!")
        except Exception as e:
             error_message.set(f"**ERROR**: {e}")


        # Reset solara elements
        name.set("Projection Name")
        SLR.set(0.0)
        RAIN.set(0.0)
        POP.set(0.0)
        ECON.set(0.0)

@solara.component
def TabProjections(m):

    update_draw_tools_none(m)
    

    with solara.Card("Projections", style={"width": "100%", "padding": "10px"}):
        solara.InputText("Projection Name", value=projName, continuous_update=True)
        solara.Markdown(f"**Your Projection Name**: {projName.value}")
        solara.InputFloat("Sea Level Rise [m]", value=SLR_input, continuous_update=True)
        solara.InputFloat("Precipitation Increase [%]", value=RAIN_input, continuous_update=True)
        solara.InputFloat("Population Growth [%]", value=POP_input, continuous_update=True)
        solara.InputFloat("Economic Growth [%]", value=ECON_input, continuous_update=True)
        
        def save():
            _save_inputs_projections(
                name=projName, 
                SLR=SLR_input, 
                RAIN=RAIN_input, 
                POP=POP_input, 
                ECON=ECON_input,
                output_message=output_message,
                error_message=error_message
                )

        solara.Button("Save Inputs", on_click=save, style={"margin-top": "20px"})

        if output_message.value:
            solara.Markdown(f"**{output_message.value}**")
        if error_message.value:
            solara.Markdown(f"{error_message.value}", style={"color", "red"})