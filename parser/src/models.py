from .database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Vacancies(Base):
    __tablename__ = "vakansii hh.ru"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    salary: Mapped[str]
    skills: Mapped[str]
    schedule: Mapped[str]
    experience: Mapped[str]
    region: Mapped[str]
    address: Mapped[str]#параметры/атрибуты класса
    #создание полей для таблицы