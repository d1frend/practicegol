from .database import Base, engine


def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

