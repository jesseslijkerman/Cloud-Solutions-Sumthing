from sqlalchemy import DateTime, Column, Integer, String
from database import Base

class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True, index=True)
    bucket = Column(String(100))
    bucket_original = Column(String(100))
    date = Column(DateTime(20))
    longitude = Column(Integer)
    latitude = Column(Integer)
