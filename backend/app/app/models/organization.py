from sqlalchemy import Column, Integer, String, DateTime,Boolean,Text
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Organization(Base):
    id = Column(Integer,primary_key=True)
    name = Column(String(200))
    personal = Column(Boolean)
    setting = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status=Column(TINYINT,comment="-1->delete,1->active,0->inactive")

    member = relationship("Member",back_populates="organization")
    role = relationship("Role",back_populates="organization")

