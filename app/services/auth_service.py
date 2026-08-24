from app.models import User, StudentProfile
from app.core.security import hash_password, verify_password, create_access_token
def register(db,email,password,first_name,last_name):
 if len(password) < 8 or len(password) > 72: raise ValueError('password')
 if db.query(User).filter_by(email=email).first(): raise ValueError('exists')
 u=User(email=email,password_hash=hash_password(password),role='STUDENT'); db.add(u); db.flush(); db.add(StudentProfile(user_id=u.id,first_name=first_name,last_name=last_name)); db.commit(); db.refresh(u); return u,create_access_token(str(u.id),u.role)
def login(db,email,password):
 u=db.query(User).filter_by(email=email).first()
 if not u or not verify_password(password,u.password_hash): return None
 return u,create_access_token(str(u.id),u.role)
