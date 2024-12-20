
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Employer(Base):
    __tablename__ = 'wp_measures'
    id = Column(Integer, primary_key=True)
