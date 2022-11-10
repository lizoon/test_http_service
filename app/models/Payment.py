from app import *

import sqlalchemy as sqa
from sqlalchemy import Integer, String, Date, DateTime


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    sum = Column(Integer, nullable=False)
    payment_date = Column(Date, nullable=False)
    type_id = Column(ForeignKey("dictionary.id", ondelete="CASCADE"), index=True)
    credit_id = Column(ForeignKey("credits.id", ondelete="CASCADE"), index=True)

    credit = relationship("Credit")
    type = relationship("Dictionary")
