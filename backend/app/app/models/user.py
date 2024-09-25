from sqlalchemy import Column, Integer, String, DateTime,Text
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    id = Column(Integer,primary_key=True)
    email = Column(String(255))
    phone = Column(String(20))
    password = Column(String(255))
    profile =Column(Text)
    created_at=Column(DateTime)
    updated_at=Column(DateTime)
    status=Column(TINYINT,comment="-1->delete,1->active,0->inactive")

    member = relationship("Member",back_populates="user")



    
    
    
    
