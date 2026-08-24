from app.models import *
def profile(db,u):
 p=u.profile; counts={k:db.query(m).filter_by(student_id=u.id).count() for k,m in [('skills',StudentSkill),('projects',StudentProject),('certifications',StudentCertification),('achievements',StudentAchievement),('internships',StudentInternship)]}; roles=db.query(StudentPreferredRole).filter_by(student_id=u.id).all(); resume=db.query(StudentDocument).filter_by(student_id=u.id,document_type='RESUME',is_active=True).first(); return {'user':{'id':str(u.id),'email':u.email,'role':u.role},'profile':p,'counts':counts,'preferred_roles':roles,'resume':resume}
def completeness(db,u):
 p=u.profile; score=0; missing=[]
 if p.first_name and p.last_name: score+=15
 else: missing.append('basic_information')
 if all([p.department,p.degree,p.institution_name,p.graduation_year,p.cgpa is not None]): score+=15
 else: missing.append('academic_details')
 if p.phone and p.city: score+=10
 else: missing.append('contact_information')
 n=db.query(StudentSkill).filter_by(student_id=u.id).count(); score += 20 if n>=5 else 15 if n>=3 else 10 if n else 0
 if not n: missing.append('skills')
 for key,m,w in [('projects',StudentProject,10),('certifications',StudentCertification,10),('internships',StudentInternship,5)]:
  if db.query(m).filter_by(student_id=u.id).count(): score+=w
  else: missing.append(key)
 if db.query(StudentDocument).filter_by(student_id=u.id,document_type='RESUME',is_active=True).first(): score+=10
 else: missing.append('resume')
 if db.query(StudentPreferredRole).filter_by(student_id=u.id).count(): score+=5
 else: missing.append('preferred_roles')
 return {'score':score,'missing_sections':missing}
