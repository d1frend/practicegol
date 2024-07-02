from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

engine = create_engine(
    url=settings.database_url_psycopg,
    pool_pre_ping=True,
)
#создание движка для бд

session_factory = sessionmaker(engine)#создаю сессии, чтобы делать запросы в бд

class Base(DeclarativeBase):
    pass