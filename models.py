from sqlalchemy import Column, Integer, String
from database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    country = Column(String)
    state = Column(String)
    district = Column(String)
    area = Column(String)
    experience = Column(Integer)
    qualification = Column(String)
    job_category = Column(String)
    job_role = Column(String)
    resume = Column(String)
    result = Column(String)
