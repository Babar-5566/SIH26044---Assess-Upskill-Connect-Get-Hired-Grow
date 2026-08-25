from pydantic import BaseModel, EmailStr, Field
class RegisterStudent(BaseModel): email:EmailStr; password:str=Field(min_length=8,max_length=72); first_name:str; last_name:str
class Login(BaseModel): email:EmailStr; password:str=Field(min_length=1,max_length=72)
class UserOut(BaseModel): id:str; email:str; role:str; is_active:bool
class Token(BaseModel): access_token:str; token_type:str='bearer'
