import solara
from ipyleaflet import GeomanDrawControl
from IPython.display import display

from draw_utils import _handle_draw, draw_map

check_floodmap = solara.reactive(False)
check_damages = solara.reactive(False)
check_metrics = solara.reactive(False)
check_metrics_static = solara.reactive(False)

def _on_checkbox_change(checkbox, check_list):
    for check in check_list:
        if check != checkbox:
            check.set(False)

@solara.component
def TabVisualisation(m, TAB, GEOM):
    with solara.Card("Map Visualisation", style={"width": "100%", "padding": "10px"}):

        error_message = solara.use_reactive("")

        check_list = [
            check_floodmap,
            check_damages,
            check_metrics,
        ]

        def handle_draw(self, action, geo_json):
            _handle_draw(self, action, geo_json, GEOM)

        def on_checkbox_change(check):
            _on_checkbox_change(check, check_list=check_list)


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
            m = draw_map()

        display(m)
        
        if error_message.value:
            solara.Markdown(f"{error_message}", style={"color": "red"})
        solara.Markdown("<span style='color: #4682B4;'><b>Please Note:</b> The  generation of figures may take some seconds.</span>")
        solara.Markdown("If Metrics do not show, select the static option.")
        solara.Markdown("**Selection**:")
        solara.Checkbox(label="Floodmap", value=check_floodmap, on_value=lambda v: on_checkbox_change(check_floodmap) if v else None)
        solara.Checkbox(label="Building Damages", value=check_damages, on_value=lambda v: on_checkbox_change(check_damages) if v else None)
        solara.Checkbox(label="Metrics", value=check_metrics, on_value=lambda v: on_checkbox_change(check_metrics) if v else None)
        if check_metrics.value:
            with solara.Div(style={"margin-left": "20px"}): 
                solara.Checkbox(label="Metrics (static)", value=check_metrics_static, on_value=lambda v: on_checkbox_change(check_metrics) if v else None)

        solara.Markdown(f"**Selected Geoms**: {GEOM.value}")
