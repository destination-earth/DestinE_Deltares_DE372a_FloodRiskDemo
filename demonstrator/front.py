import solara

from flood_adapt.api.static import read_database
from flood_adapt.misc.config import Settings, UnitSystem

from demonstrator.tabs.event_tab import TabEvent
from demonstrator.tabs.projection_tab import TabProjections
from demonstrator.tabs.measure_tab import TabMeasures
from demonstrator.tabs.strategy_tab import TabStrategy
from demonstrator.tabs.scenario_tab import TabScenario
from demonstrator.tabs.run_tab import TabRun
from demonstrator.tabs.vis_tab import TabVisualisation
from demonstrator.utils.draw_utils import draw_map_controls
from demonstrator.utils.plot_utils import plot_metrics

@solara.component
def Page(database_fn, unit_system="metric"):

    view = solara.use_reactive(None)
    tab = solara.use_reactive("Event")
    geom = solara.use_reactive(None)
    scenario_metrics = solara.use_reactive(None)

    units = UnitSystem(system=unit_system)
    Settings(
        DATABASE_ROOT=database_fn.parent,
        DATABASE_NAME=database_fn.stem,
        SYSTEM_FOLDER=database_fn/"system",
        unit_system=units
    )

    db = read_database(database_path=database_fn.parent, site_name=database_fn.stem)
    center = (db.site.attrs.lat, db.site.attrs.lon)


    m = draw_map_controls(center)

    with solara.Columns():
        with solara.Column(style={"object-fit": "scale-down"}):
            TabVisualisation(m, tab, geom, scenario_metrics)

        with solara.Column(style={"display": "flex", "flex_flow": "flex-wrap"}):
            SettingsTabs(selected_tab=tab, selected_view=view, selected_geom=geom)

    if scenario_metrics.value is not None:
        plot_metrics(scenario_metrics.value)

    
@solara.component
def SettingsTabs(selected_tab, selected_view, selected_geom):

    with solara.Row(style={"justify-content": "flex-start","display": "flex", "flex_flow": "flex-wrap"}):
        solara.Button("Event", on_click=lambda: (selected_tab.set('Event'), selected_view.set(None)))
        solara.Button("Projections", on_click=lambda: (selected_tab.set('Projections'), selected_view.set(None)))
        solara.Button("Measures", on_click=lambda: (selected_tab.set('Measures'), selected_view.set(None)))
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


