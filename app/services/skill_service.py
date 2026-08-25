from app.models import Skill,StudentSkill
def add(db,u,data):
 n=data.name.strip().lower(); s=db.query(Skill).filter_by(normalized_name=n).first()
 if not s: s=Skill(name=data.name.strip(),normalized_name=n,skill_type=data.skill_type); db.add(s); db.flush()
 if db.query(StudentSkill).filter_by(student_id=u.id,skill_id=s.id).first(): raise ValueError('exists')
 x=StudentSkill(student_id=u.id,skill_id=s.id,proficiency_level=data.proficiency_level,score=data.score); db.add(x); db.commit(); db.refresh(x); return x
