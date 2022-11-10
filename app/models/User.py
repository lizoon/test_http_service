from app import *

import sqlalchemy as sqa
from sqlalchemy import Integer, String, Date, DateTime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String(255), nullable=False)
    registration_date = Column(Date, nullable=False)
