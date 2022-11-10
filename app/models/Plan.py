from app import *

import sqlalchemy as sqa
from sqlalchemy import Integer, String, Date, DateTime


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, server_default=text("nextval('id_seq')"))
    period = Column(Date)
    sum = Column(Integer)
    category_id = Column(ForeignKey("dictionary.id", ondelete="CASCADE"))

    category = relationship("Dictionary")
