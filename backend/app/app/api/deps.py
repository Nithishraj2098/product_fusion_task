
from typing import Generator, Any, Optional
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
import hashlib
from app.core.config import settings
from fastapi import Depends, HTTPException, status
from jose import jwt
from pydantic import ValidationError
import schemas


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()




def verify_hash(hash_data:str, included_variable:str):

    included_variable = (included_variable + settings.SALT_KEY).encode("utf-8")
    real_hash = hashlib.sha1(included_variable).hexdigest()
    if hash_data == real_hash:
        return True
        
    return False




def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> models.Member:
    # token = "$2b$12$YjUlPhD9tiNgfpAb61atleGvOUXRlY6Elkjb89MaNBJlAUWxibS7i"
    print(token)
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=[{"msg":"Could not validate credentials"}],
        )
    user = get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail=[{"msg":"User not found"}])
    return user

def get(db: Session, id: Any) -> Optional[models.Member]:
    user = db.query(models.Member).filter(models.Member.user_id == id, models.Member.status == 1).first()
    return user

