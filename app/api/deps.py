from fastapi import Depends, HTTPException
from uuid import UUID
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
from app.core.security import decode_token
bearer=HTTPBearer(auto_error=False)
def get_current_user(credentials=Depends(bearer), db:Session=Depends(get_db)):
 if not credentials: raise HTTPException(401,"Unauthorized")
 p=decode_token(credentials.credentials)
 if not p or not p.get('sub'):
  raise HTTPException(401,"Unauthorized")
 try: user_id = UUID(str(p['sub']))
 except (ValueError, TypeError): raise HTTPException(401,"Unauthorized")
 u=db.get(User,user_id)
 if not u or not u.is_active: raise HTTPException(401,"Unauthorized")
 return u
def require_roles(*roles):
 def dep(user=Depends(get_current_user)):
  if user.role not in roles: raise HTTPException(403,"Forbidden")
  return user
 return dep
