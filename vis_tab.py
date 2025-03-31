import solara
from ipyleaflet import GeomanDrawControl
from IPython.display import display

from flood_adapt.api.scenarios import get_scenarios
from flood_adapt.dbs_classes.database import Database

from draw_utils import _handle_draw, draw_map
from plot_utils import plot_floodmap, plot_damage_agg, plot_damage_build

def _on_checkbox_change(checkbox, check_list):
    for check in check_list:
        if check != checkbox:
            check.set(False)

@solara.component
def TabVisualisation(m, TAB, GEOM, SCEN_TOGGLE):

    selected_scenario = solara.use_reactive(SCEN_TOGGLE.value)
    check_floodmap = solara.use_reactive(None)
    check_damages_agg = solara.use_reactive(None)
    check_damages_build = solara.use_reactive(None)
    check_metrics = solara.use_reactive(bool(SCEN_TOGGLE.value))

    scenarios = [scen.attrs.name for scen in get_scenarios()["objects"] if scen.has_run_check()]

    center = (Database().site.attrs.lat, Database().site.attrs.lon)

    with solara.Card("Map Visualisation", style={"width": "100%", "padding": "10px"}):

        error_message = solara.use_reactive("")

        check_list_hazard = [
            check_floodmap,
        ]
        
        check_list_impact = [
            check_damages_agg,
            check_damages_build,
            check_metrics
        ]

        def handle_draw(self, action, geo_json):
            _handle_draw(self, action, geo_json, GEOM)

        def on_checkbox_change_hazard(check):
            _on_checkbox_change(check, check_list=check_list_hazard)
        
        def on_checkbox_change_impact(check):
            _on_checkbox_change(check, check_list=check_list_impact)


        if TAB.value == "Measures":
            for control in m.controls:
                if isinstance(control, GeomanDrawControl):
                    control.on_draw(handle_draw)
                        
        else:
            GEOM.set(None)
            for control in m.controls:
                if isinstance(control, GeomanDrawControl):
                    m.remove(control)
            m.add(GeomanDrawControl())
            m = draw_map(center)

        display(m)
        
        if error_message.value:
            solara.Markdown(f"{error_message}", style={"color": "red"})
        
        solara.Select(label="Select scenario to visualize", value=selected_scenario, values=["None", *scenarios])

        if selected_scenario.value in scenarios:

            solara.Markdown("Note: rendering plots may take a minute.", style={"color": "#4682B4"})

            with solara.Row():
                solara.Checkbox(label="Floodmap", value=check_floodmap, on_value=lambda v: on_checkbox_change_hazard(check_floodmap) if v else None)
                solara.Checkbox(label="Damage Aggregate", value=check_damages_agg, on_value=lambda v: on_checkbox_change_impact(check_damages_agg) if v else None)
                solara.Checkbox(label="Damage Buildings", value=check_damages_build, on_value=lambda v: on_checkbox_change_impact(check_damages_build) if v else None)
                solara.Checkbox(label="Metrics", value=check_metrics, on_value=lambda v: SCEN_TOGGLE.set(selected_scenario.value) if v else SCEN_TOGGLE.set(None))

            if check_floodmap.value:
                plot_floodmap(m, selected_scenario.value)
            if check_damages_agg.value:
                plot_damage_agg(m, selected_scenario.value)
            if check_damages_build.value:
                plot_damage_build(m, selected_scenario.value)
