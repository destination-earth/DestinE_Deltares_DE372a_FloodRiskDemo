import solara
from ipyleaflet import Map, DrawControl, basemaps
from IPython.display import display

from event_tab import TabEvent
from projection_tab import TabProjections
from measure_tab import TabMeasures
from strategy_tab import TabStrategy
from scenario_tab import TabScenario
from run_tab import TabRun
from vis_tab import TabVisualisation
from draw_utils import handle_draw

view = solara.reactive(None)
tab = solara.reactive('Event') 


@solara.component
def Page(database):

    m = Map(center=(52.08654741528378, 4.295223531699989), zoom=10, scroll_wheel_zoom=True, basemap=basemaps.OpenStreetMap.Mapnik)

    draw_control = DrawControl(
        polyline={'shapeOptions': {'color': 'blue', 'weight': 4}},
        polygon={'shapeOptions': {'color': 'red', 'weight': 4}},
        marker={},
        rectangle={},  
        circle={},
    )

    draw_control.on_draw(handle_draw)
    m.add_control(draw_control)

    with solara.Columns():
        with solara.Column(style={"width": "70%", "min-width": "650px"}):
            display(m) 

        with solara.Column(style={"width": "30%", "min-width": "500px"}):
            SettingsTabs(m, database, selected_tab=tab, selected_view=view)

@solara.component
def SettingsTabs(m, database, selected_tab, selected_view):
    with solara.Column(style={"width": "100%", "align-items": "center"}):
        with solara.Row(gap="10px", style={"justify-content": "flex-start", "width": "80%"}):
            solara.Button("Event", on_click=lambda: (selected_tab.set('Event'), selected_view.set(None)))
            solara.Button("Projections", on_click=lambda: (selected_tab.set('Projections'), selected_view.set(None)))
            solara.Button("Measures", on_click=lambda: (selected_tab.set('Measures'), selected_view.set(None)))
        with solara.Row(gap="10px", style={"justify-content": "flex-start", "width": "80%"}):
            solara.Button("Strategy", on_click=lambda: (selected_tab.set('Strategy'), selected_view.set(None)))
            solara.Button("Scenario", on_click=lambda: (selected_tab.set('Scenario'), selected_view.set(None)))
        with solara.Row(gap="10px", style={"justify-content": "flex-start", "width": "80%"}):
            solara.Button("Run", on_click=lambda: (selected_tab.set('Run'), selected_view.set(None)))
            solara.Button("Visualisation", on_click=lambda: selected_tab.set('Visualisation'))
 
    match selected_tab.value:
        case "Event":
            TabEvent(m)
        case "Projections":
            TabProjections(m)
        case "Measures":
            TabMeasures(m)
        case "Strategy":
            TabStrategy(m)
        case "Scenario":
            TabScenario(m)
        case "Run":
            TabRun(m)
        case "Visualisation":
            TabVisualisation(m)

    # elif selected_tab.value == 'Visualisation':
    #     TabVisualisation(m)
        # mapchoice1.set(False); mapchoice2.set(False); mapchoice3.set(False)


