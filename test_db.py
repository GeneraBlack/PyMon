from pymon.core.config import Config
from pymon.core.database import Database

c = Config()
db = Database(c.db_path)
db.initialize()
print("DB initialized OK")
tables = db.conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()
print(f"{len(tables)} tables:", [t[0] for t in tables])
db.close()
