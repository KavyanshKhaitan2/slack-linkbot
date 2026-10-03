from datetime import UTC, datetime

from sqlmodel import Field, Session, SQLModel, create_engine

import settings


def utcnow() -> datetime:
    return datetime.now(UTC)


# 1. Define the Model (Acts as both Pydantic schema and DB Table)
class PendingAccountLink(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)
    parent_slack_id: str
    token: str = Field(unique=True)

class AccountLink(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)
    parent_slack_id: str
    child_slack_id: str

# 2. Setup the DB Connection
db_url = settings.DB_URL
engine = create_engine(db_url, echo=True)

# Create tables
SQLModel.metadata.create_all(engine)

# 3. Use inside a Database Session
# with Session(engine) as session:
#     new_hero = Hero(name="Deadpond", secret_name="Dive Wilson")
#     session.add(new_hero)
#     session.commit()
#     session.refresh(new_hero)
#    print(f"Created hero: {new_hero.name} with ID {new_hero.id}")
