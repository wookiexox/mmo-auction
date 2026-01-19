from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer)

    # race condition
    is_sold = Column(Boolean, default=False)
    owner_id = Column(Integer, nullable=True)
