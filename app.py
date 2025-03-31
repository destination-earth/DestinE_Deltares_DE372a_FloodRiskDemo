import solara
from pathlib import Path
import demonstrator.front as front

db_path = Path(r"C:\Users\tromp_wm\fa_databases\scheveningen")

@solara.component
def Page():

    front.Page(database_fn=db_path)