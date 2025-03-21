import solara

from event_tab import TabEvent
from projection_tab import TabProjections
from measure_tab import TabMeasures
from strategy_tab import TabStrategy
from scenario_tab import TabScenario
from run_tab import TabRun
from vis_tab import TabVisualisation
from draw_utils import draw_map_controls

@solara.component
def Page(database):

    view = solara.use_reactive(None)
    tab = solara.use_reactive("Event")
    geom = solara.use_reactive(None)

    m = draw_map_controls()

    with solara.Columns():
        with solara.Column(style={"width": "70%", "min-width": "650px"}):
            TabVisualisation(m, tab, geom)

        with solara.Column(style={"width": "30%", "min-width": "500px"}):
            SettingsTabs(selected_tab=tab, selected_view=view, selected_geom=geom)

@solara.component
def SettingsTabs(selected_tab, selected_view, selected_geom):
    with solara.Column(style={"width": "100%", "align-items": "center"}):
        with solara.Row(gap="10px", style={"justify-content": "flex-start", "width": "80%"}):
            solara.Button("Event", on_click=lambda: (selected_tab.set('Event'), selected_view.set(None)))
            solara.Button("Projections", on_click=lambda: (selected_tab.set('Projections'), selected_view.set(None)))
            solara.Button("Measures", on_click=lambda: (selected_tab.set('Measures'), selected_view.set(None)))
        with solara.Row(gap="10px", style={"justify-content": "flex-start", "width": "80%"}):
            solara.Button("Strategy", on_click=lambda: (selected_tab.set('Strategy'), selected_view.set(None)))
            solara.Button("Scenario", on_click=lambda: (selected_tab.set('Scenario'), selected_view.set(None)))
            solara.Button("Run", on_click=lambda: (selected_tab.set('Run'), selected_view.set(None)))            
 
    match selected_tab.value:
        case "Event":
            TabEvent()
        case "Projections":
            TabProjections()
        case "Measures":
            TabMeasures(selected_geom)
        case "Strategy":
            TabStrategy()
        case "Scenario":
            TabScenario()
        case "Run":
            TabRun()


