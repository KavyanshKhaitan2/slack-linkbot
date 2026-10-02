from sqlmodel import Field, Session, SQLModel, create_engine, select


# 1. Define the Model (Acts as both Pydantic schema and DB Table)
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = None

# 2. Setup the DB Connection
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, echo=True)

# Create tables
SQLModel.metadata.create_all(engine)

# 3. Use inside a Database Session
with Session(engine) as session:
    new_hero = Hero(name="Deadpond", secret_name="Dive Wilson")
    session.add(new_hero)
    session.commit()
    session.refresh(new_hero)
    print(f"Created hero: {new_hero.name} with ID {new_hero.id}")
