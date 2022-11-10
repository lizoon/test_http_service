from app import *

import sqlalchemy as sqa
from sqlalchemy import Integer, String, Date, DateTime


class Credit(Base):
    __tablename__ = "credits"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"))
    issuance_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=False)
    actual_return_date = Column(Date, nullable=True)
    body = Column(Integer)
    percent = Column(Float(53))

    user = relationship("User")
