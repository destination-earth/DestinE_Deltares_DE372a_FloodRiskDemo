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

    with solara.Column():

        with solara.AppBarTitle():
            solara.lab.ThemeToggle()
            solara.Text("Demonstrator")
        
        with solara.Sidebar():
            SettingsTabs(selected_tab=tab, selected_geom=geom)
        with solara.Column():

            TabVisualisation(m, tab, geom, scenario_metrics)

            if scenario_metrics.value is not None:
                plot_metrics(scenario_metrics.value)

    
@solara.component
def SettingsTabs(selected_tab, selected_geom):
    tab_index = solara.use_reactive(0)
    tabs = [
        "Event",
        "Projections",
        "Measures",
        "Strategy",
        "Scenario",
        "Run"
    ]

    with solara.lab.Tabs(value=tab_index, lazy=True, background_color="primary", dark=True):
        selected_tab.set(tabs[tab_index.value])
        with solara.lab.Tab("Event"):
            TabEvent()
        with solara.lab.Tab("Projections"):
            TabProjections()     
        with solara.lab.Tab("Measures"):
            TabMeasures(selected_geom)
        with solara.lab.Tab("Strategy"):
            TabStrategy()
        with solara.lab.Tab("Scenario"):
            TabScenario()
        with solara.lab.Tab("Run"):
            TabRun()


