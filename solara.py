import solara
from pathlib import Path
import app_main

db_path = Path(r"C:\Users\tromp_wm\fa_databases\scheveningen")

@solara.component
def Page():
    
    app_main.Page(database_fn=db_path)