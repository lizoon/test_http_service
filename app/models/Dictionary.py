from app import *

import sqlalchemy as sqa
from sqlalchemy import Integer, String, Date, DateTime


class Dictionary(Base):
    __tablename__ = "dictionary"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
