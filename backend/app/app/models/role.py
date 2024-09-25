from sqlalchemy import Column, Integer, String, ForeignKey,Text
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Role(Base):
    id = Column(Integer,primary_key=True)
    org_id = Column(Integer,ForeignKey("organization.id"))
    name= Column(String(200))
    description = Column(Text)
    status = Column(TINYINT,comment="2->owner,1->member active,0-> inactive,-1->deleted")

    member = relationship("Member",back_populates="role")
    organization = relationship("Organization",back_populates="role")

    