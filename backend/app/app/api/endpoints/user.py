
from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.models import User
from app.api import deps
from app.core.security import get_password_hash,verify_password
from datetime import datetime
from app.utils import *
from sqlalchemy import func

import random


router = APIRouter()

@router.post("/reset_password")
async def resetPassword(db:Session=Depends(deps.get_db),
                        new_password:str=Form(...),
                        confirm_password:str=Form(...),
                        memberID:int=Form(...),
                        current_user:Member=Depends(deps.get_current_user)):
    
    """ Reset password is to Admin can change the password of other members"""
    if current_user:
        # getOrg = db.query(Member.org_id).filter(Member.user_id == current_user.id,
        #                                  Member.status ==1).first()
        org_id  = current_user.org_id #if getOrg else None

        if not org_id:
            return {"status":0,"msg":"No organization found."}
        else:
            checkMember =  db.query(Member).filter(Member.id == memberID,
                                                   Member.org_id == org_id,
                                                   Member.status ==1).first()
            if not checkMember:
                return {"status":0,"msg":"No member details found"}
            else:
                if new_password != confirm_password:
                    return {"status":0,"msg":"Password not match"}
                else:
                    checkMember.user.password = get_password_hash(new_password)
                    db.commit()
                    msg ="""Your password was reset by admin .
                            Please make sure you having updated password while login."""
                    res = await send_mail(receiver_email=checkMember.user.email,message=msg)
                    return {"status":1,"msg":"Password changed successfully"}
    else:
        return {"status":-1,"msg":"You are not authorized to perform this action"}


@router.post("/change_password")
async def changePassword(db:Session=Depends(deps.get_db),
                         current_user:Member=Depends(deps.get_current_user),
                         old_password:str=Form(...),
                         new_password:str=Form(...)):
    """User changes password by self"""
    if current_user:
        if verify_password(old_password,current_user.user.password):
            current_user.user.password= get_password_hash(new_password)
            db.commit()
            return {"status":1,"msg":"Your password has been changed"}
        else:
            return {"status":0,"msg":"Old password you entered is worng"}
    else:
        return {"status":-1,"msg":"You are not authorized to perform this action"}


@router.post("/invite_member")
async def inviteMember(db:Session=Depends(deps.get_db),
                        current_user:Member=Depends(deps.get_current_user),
                        email:str=Form(...),role_id:int=Form(...,description="role dropdown from dropdown.py")
                       ):
    
    """member invite link send via email
    with org_id and role id to specify the signed user 
    is belongs to this user and what role"""
    if current_user:
        if current_user.role.status ==2: #only owner can send lik
            if not check(email):
                return {"status":0,"msg":"Enter proper email"}
            checkEmail = db.query(User).\
                join(Member,Member.user_id == User.id).\
                    filter(User.email == email,
                        Member.org_id == current_user.org_id,
                            User.status ==1).first()
            if  checkEmail:
                return {"status":0,"msg":"The user belongs to this email is already in your organization."}
            else:
                checkRole= db.query(Role).\
                        filter(Role.id == role_id,
                               Role.org_id == current_user.org_id,
                               Role.status ==1 ).first()
                if not checkRole:
                    return {"status":0,"msg":"Invalid role seleted."}
                else:
                    link = f"https://www.demoCompany/signup?org_id={current_user.org_id}?role_id={role_id}?org_name={checkRole.organization.name}"


                    """ After clicking the link above assume that it navigates to
                    signup page with our customized org_id and role_id"""


                    msg = f"""Hai, Hope all are going well
                              Our beloved Owner Like you to 
                              join our organization
                              
                              
                              if you are interested please click the link below
                              
                              join now: {link}"""
                    res = await send_mail(receiver_email=email,message=msg)
                    return {"status":1,"msg":"Invite link send successfully."}
        else:
            return {"status":-1,"msg":"You are not authorized to perform this action"}
        
@router.post("/delete_member")
async def deleteMember(db:Session=Depends(deps.get_db),
                       current_user:Member=Depends(deps.get_current_user),
                       member_id:int=Form(None)):
    
    if current_user:
        checkMember = db.query(Member).filter(Member.id == member_id,
                                              Member.id !=current_user.id,
                                               Member.status ==1 ).first()
        if  checkMember:
            #-1-> belongs  to deleted logs 
            checkMember.status = -1
            checkMember.user.status = -1
            db.commit()
        else:
            return {"status":0,"msg":"Invalid member selected."}
    else:
        return {"status":-1,"msg":"You are not authorized to perform this action"}

@router.post("/update_member_role")
async def updatteMemberRole(db:Session=Depends(deps.get_db),
                        current_user:Member=Depends(deps.get_current_user),
                        member_id:int=Form(...),role_id:int=Form(...,
                                                                 description="from role dropdown in dropdown.py")):
    if current_user:
        checkMember = db.query(Member).filter(Member.id == member_id,
                                              Member.id !=current_user.id,
                                               Member.status ==1 ).first()
        if  checkMember:
            checkRole = db.query(Role).filter(Role.id == role_id,
                                              Role.org_id == current_user.org_id,
                                               Role.status ==1 ).first()
            if  checkRole:
                checkMember.role_id = role_id
                db.commit()
                return {"status":1,"msg":"Member updated successfully."}
 
            else:
                return {"staus":0,"msg":"Invalid role selected."}
        else:
            return {"status":0,"msg":"Invalid member seleted."}
    else:
        return {"status":-1,"msg":"You are not authorized to perform this action"}
    
@router.post("/create_role")
async def createRole(db:Session=Depends(deps.get_db),
                     current_user:Member=Depends(deps.get_current_user),
                     role_name:str=Form(...),description:str=Form(None)):
    if current_user:
        checkRoleName = db.query(Role).filter(Role.name == role_name,
                                              Role.status.in_([1,2]),
                                              Role.org_id == current_user.org_id).first()
        if checkRoleName:
            return {"status":0,"msg":"Role already present"}
        else:
            createTenetRole = Role(org_id =current_user.org_id,
                                    name = role_name,
                                    description =description ,
                                    status =1)
            db.add(createTenetRole)
            db.commit()

            return {"status":1,"msg":"Role added successfully."}
    else:
        return {"status":-1,"msg":"You are not authorized to perform this action"}

            


#******************************************STATS API *******************************************************************

@router.post("/role_wise_user")
async def roleWiseUser(db:Session=Depends(deps.get_db),
                       current_user:Member=Depends(deps.get_current_user),
                       role_name:str=Form(None),page:int=1,size:int=10):
    if  current_user:
        if current_user.role.status ==2 : # Organization Admin
            """ this list is for role of induvial organization"""

            get_role = db.query(Role.id,Role.name,func.count(Member.id)).\
            outerjoin(Member,Member.role_id == Role.id).\
            filter(Role.org_id == current_user.org_id, Role.status ==1)
        if  role_name:
            get_role = get_role.filter(Role.name.like("%"+role_name+"%"))
        get_role =  get_role.group_by(Role.id).order_by(Role.name.asc())

        totalCount = get_role.count()
        totalPage,offset,limit =get_pagination(totalCount,page,size)
        get_role = get_role.offset(offset).limit(limit).all()

        dataList =[]
        for rowID ,rowName,userCount in get_role:
            dataList.append({
                "role_id":rowID,
                "role_name":rowName,
                "user_count":userCount
            })
        data={"total_count":totalCount,
              "totalPage":totalPage,
              "size":size,"current_page":page,
              "items":dataList}
        return {"status":1,"msg":"Success","data":data}
    else:
        return {"status":-1,"msg":"You are not authorized to perform this action"}

@router.post("/org_members")
async def listOrgMembers(db:Session=Depends(deps.get_db),
                       current_user:Member=Depends(deps.get_current_user),
                       org_name:str=Form(None),page:int=1,size:int=10,
                       from_datetime:datetime=Form(None),
                       to_datetime:datetime=Form(None),status:int=Form(None,description="1->active,0-> inactive")):
    if  current_user:
        if to_datetime:
            to_datetime = to_datetime.replace(hour=23,minute=59,second=59)
        else:
            to_datetime =datetime.now().replace(hour=23,minute=59,second=59)
        
        if from_datetime:
            from_datetime = from_datetime.replace(hour=1,minute=0,second=0)
        else:
            from_datetime = to_datetime-timedelta(days=30)

        getAllData = db.query(Organization.id,Organization.name,func.count(Member.id)).\
        join(Member,Member.org_id == Organization.id).\
            filter(Organization.status!=-1,
                   Organization.created_at.between(from_datetime,to_datetime),
                   Member.status !=-1)
        if org_name:
            getAllData =getAllData.filter(Organization.name.like("%"+org_name+"%"))
        if status:
            getAllData =getAllData.filter(Organization.status == status)

        getAllData = getAllData.group_by(Organization.id).order_by(Organization.id.desc())

        totalCount= getAllData.count()
        totalPage,offset,limit = get_pagination(totalCount,page,size)
        getAllData = getAllData.offset(offset).limit(limit).all()

        dataList =[]

        for organizationID,orgName,memberCount in getAllData:
            dataList.append({
                "org_id":organizationID,
                "org_name":orgName,
                "member_count":memberCount
            })

        data={"total_count":totalCount,
              "totalPage":totalPage,
              "size":size,"current_page":page,
              "items":dataList}
        return {"status":1,"msg":"Success","data":data}
    else:
        return {"status":-1,"msg":"You are not authorized to perform this action"}


@router.post("/org_role_members")
async def listOrgRoleMembers(db:Session=Depends(deps.get_db),
                       current_user:Member=Depends(deps.get_current_user),
                       org_name:str=Form(None),page:int=1,size:int=10,
                       role_name:str=Form(None),
                       from_datetime:datetime=Form(None),
                       to_datetime:datetime=Form(None),status:int=Form(None,description="1->active,0-> inactive")):
    if  current_user:
        if to_datetime:
            to_datetime = to_datetime.replace(hour=23,minute=59,second=59)
        else:
            to_datetime =datetime.now().replace(hour=23,minute=59,second=59)
        
        if from_datetime:
            from_datetime = from_datetime.replace(hour=1,minute=0,second=0)
        else:
            from_datetime = to_datetime-timedelta(days=30)

        getAllData = db.query(Organization.id,Role.id,Role.name,Organization.name,func.count(Member.id)).\
        join(Member,Member.org_id == Organization.id).\
        join(Role,Role.id == Member.role_id).\
            filter(Organization.status!=-1,
                   Role.status.in_([1,2]),
                   Organization.created_at.between(from_datetime,to_datetime),
                   Member.status !=-1)
        if org_name:
            getAllData =getAllData.filter(Organization.name.like("%"+org_name+"%"))
        if status:
            getAllData =getAllData.filter(Organization.status == status)
        

        getAllData = getAllData.group_by(Organization.id,Role.id).order_by(Organization.id.desc())

        totalCount= getAllData.count()
        totalPage,offset,limit = get_pagination(totalCount,page,size)
        getAllData = getAllData.offset(offset).limit(limit).all()

        dataList =[]

        for organizationID,roleID,roleName,orgName,memberCount in getAllData:
            dataList.append({
                "org_id":organizationID,
                "org_name":orgName,
                "role_name":roleName,
                "member_count":memberCount
            })

        data={"total_count":totalCount,
              "totalPage":totalPage,
              "size":size,"current_page":page,
              "items":dataList}
        return {"status":1,"msg":"Success","data":data}
    else:
        return {"status":-1,"msg":"You are not authorized to perform this action"}
        
        
        



        







