from fastapi import FastAPI

from sqlalchemy import Column, Date, Float, ForeignKey, String, Integer, text
from sqlalchemy.orm import relationship

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

url = "postgresql+psycopg2://liza:liza_kisya@barbak.cyou:5432/liza"


engine = create_engine(url)
Base = declarative_base()

from app.models.User import User
from app.models.Credit import Credit
from app.models.Payment import Payment
from app.models.Plan import Plan
from app.models.Dictionary import Dictionary

# create tables
Base.metadata.create_all(bind=engine)

# connection to db
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

app = FastAPI()

# routes
from app.routes.main import *
from app.routes.additional import *
