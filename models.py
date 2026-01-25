from sqlalchemy import Column, Integer, String, Text
from database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    role = Column(String)
    q1 = Column(Text)
    q2 = Column(Text)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
