from db import DB
from ui import UI


def setup():
    db = DB('pinged.db')
    db.migrate()
    ui = UI(db)
    ui.root.mainloop()

setup()
