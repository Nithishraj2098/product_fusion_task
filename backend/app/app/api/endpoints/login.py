
from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.models import User
from app.api import deps
from app.core.security import get_password_hash,verify_password,create_access_token
from datetime import datetime
from app.utils import *
from sqlalchemy import or_

import random


router = APIRouter()

"""Sign_in after a successful signup """
@router.post("/login/access-token")
async def login(db:Session = Depends(deps.get_db)
                ,username:str=Form(...,description="email id"),
                password:str=Form(...)):

    user_name = username.strip()
    pwd = password.strip()
    
    getUser = db.query(User).filter(
        User.email == user_name,
        User.status == 1 ).first()
    
    if getUser:
        if not getUser.password:
            # Status -> 0 indicates error msg
            return {"status": 0, "msg": "User has not updated password yet."}
        
        if not verify_password(pwd, getUser.password):
            return {"status": 0, "msg": "Invalid password."}
        
        token = create_access_token(getUser.id)  # Ensure data structure is correct
        msg ="""Welcome back.
                Have a good day
                
                if the the login was not by you. Please update the password ,
                and dont share with anyone"""
        res = await send_mail(receiver_email=getUser.email,message=msg)
        return {
            "access_token": token,
            "token_type": "bearer",
            "status": 1,
            "msg": "Successful login",
            "user_name": username
        }
    else:
        return {"status": 0, "msg": "Invalid username."}
    
@router.post("/signup")
async def signup(db:Session=Depends(deps.get_db),
                 org_id:int=Form(None,description="if the user signup via referal link"),
                 role_id:int=Form(None,description="if the user signup via referal link"),
                 email:str=Form(...),phone:str=Form(...),
                 password:str=Form(...),confirm_password:str=Form(...),
                 organization_name:str=Form(...)):
    if not check(email):
        return {"status":0,"msg":"Enter valid email"}
    checkEmail = db.query(User).filter(or_(User.email == email,
                                           User.phone == phone),
                                        User.status ==1).first()
    if checkEmail:
        return {"status":0,"msg":"Email/phone number already in use."}
    else:
        if password != confirm_password:
            return {"status":0,"msg":"Password not matched"}
        
        if not org_id:
            create_org =Organization(name = organization_name,
                                    personal =1, 
                                    created_at = datetime.now(), 
                                    status=1 )
            db.add(create_org)
            db.commit()
            org_id = create_org.id
        else:
            check_org = db.query(Organization).filter(Organization.id ==org_id,
                                                      Organization.status ==1 ).first()
            if  not check_org:
                return {"status":0,"msg":"No organization details found."}
        if org_id and role_id:
            checkRoleID = db.query(Role).filter(Role.id ==role_id,
                                                 Role.org_id ==org_id,
                                                  Role.status ==1 ).first()
            if not checkRoleID:
                return {"status":0,"msg":"Invalid role assigned to ypu .Please contact with admin for further access."}
        create_user = User(email = email,
                           phone = phone,
                           password = get_password_hash(password),
                           created_at = datetime.now(),
                           status =1)
        db.add(create_user)
        db.commit()
        if not role_id:
            createOwnerRole = Role(org_id =org_id,
                                    name = "Owner",
                                    description = "One who 1st signed up",
                                    status =2)
            db.add(createOwnerRole)
            db.commit()

            createTenetRole = Role(org_id =org_id,
                                    name = "Tenet",
                                    description = "One who is under the owner",
                                    status =1)
            db.add(createTenetRole)
            db.commit()
            
            role_id = createOwnerRole.id
        
        addMember = Member(org_id = org_id,
                            user_id = create_user.id,
                            role_id = role_id,
                            created_at = datetime.now(),
                            status =1)
        db.add(addMember)
        db.commit()
        if not org_id:
            link = f"https://www.demoCompany/signup?org_id={org_id}?role_id={addMember.id}?org_name={organization_name}"
            msg =f"""Thanks for joining our organization
                    Have a good day
                    
                    You are having a Owner role
                    
                    invite your members using below link
                    invite link: {link}"""
        else:
            msg = """Thanks for joining our organization
                      Have a good day"""
        res = await send_mail(receiver_email=email,message=msg)
        return {"status":1,"msg":"successfully signed up."}
