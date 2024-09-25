
from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.api import deps
from app.utils import *


import random


router = APIRouter()

@router.post("/role_dropdown")
async def roledropDown(db:Session=Depends(deps.get_db),
                       current_user:Member=Depends(deps.get_current_user),
                       role_name:str=Form(None)):
    if current_user:
        get_role = db.query(Role.id,Role.name).\
            filter(Role.org_id == current_user.org_id,
                   Role.status ==1)
        if  role_name:
            get_role = get_role.filter(Role.name.like("%"+get_role+"%"))
        get_role = get_role.all()

        dataList =[]
        for rowID ,rowName in get_role:
            dataList.append({
                "role_id":rowID,
                "role_name":rowName
            })
        return {"status":1,"msg":"Success","data":dataList}
    else:
        return {"status":-1,"msg":"You are not authorized to perform this action"}
    

@router.post("/member_dropdown")
async def memberdropDown(db:Session=Depends(deps.get_db),
                       current_user:Member=Depends(deps.get_current_user),
                       ):
    if current_user:
        get_user = db.query(User.id,User.email).\
        join(Member,Member.user_id == User.id).\
            filter(User.status ==1,
                   Member.org_id == current_user.org_id)
        
        get_user = get_user.all()

        dataList =[]
        for rowID ,rowName in get_user:
            dataList.append({
                "role_id":rowID,
                "role_name":rowName
            })
        return {"status":1,"msg":"Success","data":dataList}
    else:
        return {"status":-1,"msg":"You are not authorized to perform this action"}
