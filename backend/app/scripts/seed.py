from app.db.session import SessionLocal
from app.models import User, StudentProfile, Skill, CareerRole
from app.core.security import hash_password
SKILLS=['Java','Python','SQL','Spring Boot','REST API','Docker','HTML','CSS','JavaScript','Communication','Problem Solving','Data Analysis']
ROLES=['Java Backend Developer','Frontend Developer','Full Stack Developer','Data Analyst','Data Scientist','Cloud Engineer','DevOps Engineer']
def main():
    db=SessionLocal()
    accounts = [('admin.test@example.com','admin@123','ADMIN'),('student.test@gmail.com','student@123','STUDENT'),('industry.admin.test@example.com','industry@123','INDUSTRY_ADMIN'),('recruiter.test@example.com','recruiter@123','INDUSTRY_MEMBER_RECRUITER'),('institution.admin.test@example.com','institution@123','INSTITUTION_ADMIN'),('faculty.test@example.com','faculty@123','FACULTY'),('mentor.test@example.com','mentor@123','MENTOR_TRAINER')]
    for email,pw,role in accounts:
        u=db.query(User).filter_by(email=email).first()
        if not u:
            u=User(email=email,password_hash=hash_password(pw),role=role); db.add(u); db.flush()
            if role=='STUDENT': db.add(StudentProfile(user_id=u.id,first_name='Demo',last_name='Student'))
    for name in SKILLS:
        if not db.query(Skill).filter_by(normalized_name=name.lower()).first(): db.add(Skill(name=name,normalized_name=name.lower()))
    for name in ROLES:
        if not db.query(CareerRole).filter_by(normalized_name=name.lower()).first(): db.add(CareerRole(name=name,normalized_name=name.lower()))
    db.commit(); db.close()
if __name__=='__main__': main()
