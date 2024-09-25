from sqlalchemy import Column, Integer, DateTime, ForeignKey,Text
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Member(Base):
    id = Column(Integer,primary_key=True)
    org_id = Column(Integer,ForeignKey("organization.id"))
    user_id = Column(Integer,ForeignKey("user.id"))
    role_id = Column(Integer,ForeignKey("role.id"))
    setting=Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status=Column(TINYINT,comment="-1->delete,1->active,0->inactive")

    organization = relationship("Organization",back_populates="member")
    user = relationship("User",back_populates="member")
    role = relationship("Role",back_populates="member")

