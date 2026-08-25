from datetime import date
from pydantic import BaseModel, AnyUrl, Field
class ProfileUpdate(BaseModel):
 first_name:str|None=None; last_name:str|None=None; phone:str|None=None; summary:str|None=None; department:str|None=None; degree:str|None=None; institution_name:str|None=None; graduation_year:int|None=Field(None,ge=1980,le=2100); cgpa:float|None=Field(None,ge=0,le=10); city:str|None=None; state:str|None=None; linkedin_url:AnyUrl|None=None; github_url:AnyUrl|None=None; portfolio_url:AnyUrl|None=None
class ProjectIn(BaseModel): title:str; description:str|None=None; technologies:list[str]=[]; project_url:AnyUrl|None=None; start_date:date|None=None; end_date:date|None=None; status:str='IN_PROGRESS'
class CertificationIn(BaseModel): name:str; issuer:str|None=None; issue_date:date|None=None; expiry_date:date|None=None; credential_url:AnyUrl|None=None
class AchievementIn(BaseModel): title:str; description:str|None=None; achievement_date:date|None=None
class InternshipIn(BaseModel): company_name:str; role:str; description:str|None=None; start_date:date|None=None; end_date:date|None=None; status:str='ONGOING'
class SkillIn(BaseModel): name:str; skill_type:str='TECHNICAL'; proficiency_level:str='BEGINNER'; score:int|None=Field(None,ge=0,le=100)
class SkillPatch(BaseModel): proficiency_level:str|None=None; score:int|None=Field(None,ge=0,le=100)
class CareerInterestIn(BaseModel): career_role_ids:list[int]; primary_role_id:int
