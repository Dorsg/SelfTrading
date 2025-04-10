from strategy_engine.db.database import engine
from strategy_engine.db.models import Base

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")