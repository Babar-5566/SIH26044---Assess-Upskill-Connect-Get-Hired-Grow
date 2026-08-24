import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import User, StudentSkill, StudentProject, StudentCertification, StudentAchievement, StudentInternship, StudentPreferredRole, StudentDocument, Skill, CareerRole
from app.schemas.auth import RegisterStudent, Login
from app.schemas.student import ProfileUpdate, SkillIn, SkillPatch, ProjectIn, CertificationIn, AchievementIn, InternshipIn, CareerInterestIn
from app.services import auth_service, student_service, skill_service, resume_service
from app.core.response import success
from app.core.config import settings

router = APIRouter()

def serialize(value):
    if value is None or isinstance(value, (str, int, float, bool)): return value
    if isinstance(value, uuid.UUID): return str(value)
    if isinstance(value, list): return [serialize(x) for x in value]
    if isinstance(value, dict): return {k: serialize(v) for k, v in value.items()}
    if hasattr(value, "__table__"): return {c.name: serialize(getattr(value, c.name)) for c in value.__table__.columns}
    return str(value)

def public_user(user: User) -> dict:
    return {"id": str(user.id), "email": user.email, "role": user.role, "is_active": user.is_active}

@router.get("/health")
def health(): return success({"status": "ok"})

auth = APIRouter(prefix="/auth", tags=["auth"])
@auth.post("/register/student", status_code=201)
def register(data: RegisterStudent, db: Session = Depends(get_db)):
    try:
        user, token = auth_service.register(db, data.email, data.password, data.first_name, data.last_name)
    except ValueError as exc:
        if str(exc) == "password": raise HTTPException(422, "Password must be between 8 and 72 characters")
        raise HTTPException(409, "Email already exists")
    return success({"user": public_user(user), "access_token": token, "token_type": "bearer"})
@auth.post("/login")
def login(data: Login, db: Session = Depends(get_db)):
    result = auth_service.login(db, data.email, data.password)
    if not result: raise HTTPException(401, "Invalid credentials")
    return success({"access_token": result[1], "token_type": "bearer"})
@auth.get("/me")
def me(user=Depends(get_current_user)): return success(public_user(user))
router.include_router(auth)

students = APIRouter(prefix="/students/me", tags=["students"])
@students.get("")
def get_profile(user=Depends(require_roles("STUDENT", "ADMIN")), db=Depends(get_db)): return success(serialize(student_service.profile(db, user)))
@students.patch("")
def update_profile(data: ProfileUpdate, user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
    for key, value in data.model_dump(exclude_unset=True).items(): setattr(user.profile, key, str(value) if "url" in key and value else value)
    db.commit(); db.refresh(user.profile); return success(serialize(student_service.profile(db, user)))
@students.get("/completeness")
def completeness(user=Depends(require_roles("STUDENT")), db=Depends(get_db)): return success(student_service.completeness(db, user))
@students.get("/dashboard")
def dashboard(user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
    profile = student_service.profile(db, user)
    return success({"profile_completeness": student_service.completeness(db, user)["score"], **profile["counts"], "has_resume": bool(profile["resume"]), "preferred_roles": serialize(profile["preferred_roles"])})

@students.get("/skills")
def list_skills(user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
    rows = db.query(StudentSkill).filter_by(student_id=user.id).all()
    return success([{**serialize(row), "skill": serialize(row.skill)} for row in rows])
@students.post("/skills", status_code=201)
def add_skill(data: SkillIn, user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
    try: row = skill_service.add(db, user, data)
    except ValueError: raise HTTPException(409, "Student already has this skill")
    return success({**serialize(row), "skill": serialize(row.skill)})
@students.patch("/skills/{item_id}")
def update_skill(item_id: uuid.UUID, data: SkillPatch, user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
    row = db.query(StudentSkill).filter_by(id=item_id, student_id=user.id).first()
    if not row: raise HTTPException(404, "Skill not found")
    for key, value in data.model_dump(exclude_unset=True).items(): setattr(row, key, value)
    db.commit(); db.refresh(row); return success(serialize(row))
@students.delete("/skills/{item_id}", status_code=204)
def delete_skill(item_id: uuid.UUID, user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
    row = db.query(StudentSkill).filter_by(id=item_id, student_id=user.id).first()
    if not row: raise HTTPException(404, "Skill not found")
    db.delete(row); db.commit()

def add_collection_routes(path, model, schema):
    @students.get(f"/{path}")
    def list_items(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
        query = db.query(model).filter_by(student_id=user.id)
        return success({"items": serialize(query.offset(skip).limit(limit).all()), "total": query.count(), "limit": limit, "skip": skip})
    @students.post(f"/{path}", status_code=201)
    def create_item(data: schema, user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
        payload = data.model_dump()
        if payload.get("start_date") and payload.get("end_date") and payload["end_date"] <= payload["start_date"]: raise HTTPException(422, "end_date must be after start_date")
        if payload.get("issue_date") and payload.get("expiry_date") and payload["expiry_date"] <= payload["issue_date"]: raise HTTPException(422, "expiry_date must be after issue_date")
        row = model(student_id=user.id, **payload); db.add(row); db.commit(); db.refresh(row); return success(serialize(row))
    @students.get(f"/{path}/{{item_id}}")
    def get_item(item_id: uuid.UUID, user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
        row = db.query(model).filter_by(id=item_id, student_id=user.id).first()
        if not row: raise HTTPException(404, "Not found")
        return success(serialize(row))
    @students.patch(f"/{path}/{{item_id}}")
    def update_item(item_id: uuid.UUID, data: schema, user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
        row = db.query(model).filter_by(id=item_id, student_id=user.id).first()
        if not row: raise HTTPException(404, "Not found")
        for key, value in data.model_dump(exclude_unset=True).items(): setattr(row, key, value)
        db.commit(); db.refresh(row); return success(serialize(row))
    @students.delete(f"/{path}/{{item_id}}", status_code=204)
    def delete_item(item_id: uuid.UUID, user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
        row = db.query(model).filter_by(id=item_id, student_id=user.id).first()
        if not row: raise HTTPException(404, "Not found")
        db.delete(row); db.commit()

add_collection_routes("projects", StudentProject, ProjectIn)
add_collection_routes("certifications", StudentCertification, CertificationIn)
add_collection_routes("achievements", StudentAchievement, AchievementIn)
add_collection_routes("internships", StudentInternship, InternshipIn)

@students.get("/career-interests")
def get_interests(user=Depends(require_roles("STUDENT")), db=Depends(get_db)): return success(serialize(db.query(StudentPreferredRole).filter_by(student_id=user.id).all()))
@students.put("/career-interests")
def put_interests(data: CareerInterestIn, user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
    if data.primary_role_id not in data.career_role_ids: raise HTTPException(422, "Primary role must be included")
    roles = db.query(CareerRole).filter(CareerRole.id.in_(data.career_role_ids), CareerRole.is_active.is_(True)).all()
    if len(roles) != len(set(data.career_role_ids)): raise HTTPException(404, "Career role not found")
    db.query(StudentPreferredRole).filter_by(student_id=user.id).delete()
    for role in roles: db.add(StudentPreferredRole(student_id=user.id, career_role_id=role.id, is_primary=role.id == data.primary_role_id))
    db.commit(); return success(serialize(db.query(StudentPreferredRole).filter_by(student_id=user.id).all()))

@students.post("/resume", status_code=201)
def upload_resume(file: UploadFile = File(...), user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
    try: path, size = resume_service.save_resume(file, user.id)
    except ValueError as exc: raise HTTPException(400, str(exc))
    db.query(StudentDocument).filter_by(student_id=user.id, document_type="RESUME", is_active=True).update({"is_active": False})
    row = StudentDocument(student_id=user.id, file_name=file.filename, file_path=str(path), file_size=size, mime_type=file.content_type)
    db.add(row); user.profile.resume_file_url = str(path); db.commit(); db.refresh(row); return success(serialize(row))
@students.get("/resume")
def get_resume(user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
    row = db.query(StudentDocument).filter_by(student_id=user.id, document_type="RESUME", is_active=True).first()
    if not row: raise HTTPException(404, "Resume not found")
    return success(serialize(row))
@students.get("/resume/download")
def download_resume(user=Depends(require_roles("STUDENT")), db=Depends(get_db)):
    row = db.query(StudentDocument).filter_by(student_id=user.id, document_type="RESUME", is_active=True).first()
    if not row or not Path(row.file_path).resolve().is_relative_to(Path(settings.upload_dir).resolve()): raise HTTPException(404, "Resume not found")
    return FileResponse(row.file_path, filename=row.file_name, media_type=row.mime_type)
router.include_router(students)

admin = APIRouter(prefix="/admin", tags=["admin"])
@admin.get("/students")
def list_students(skip: int = 0, limit: int = 20, user=Depends(require_roles("ADMIN")), db=Depends(get_db)):
    query = db.query(User).filter_by(role="STUDENT")
    return success({"items": [serialize(student_service.profile(db, row)) for row in query.offset(skip).limit(limit)], "total": query.count(), "limit": limit, "skip": skip})
@admin.get("/students/{student_id}")
def admin_student(student_id: uuid.UUID, user=Depends(require_roles("ADMIN")), db=Depends(get_db)):
    row = db.get(User, student_id)
    if not row or row.role != "STUDENT": raise HTTPException(404, "Student not found")
    return success(serialize(student_service.profile(db, row)))
router.include_router(admin)

meta = APIRouter(prefix="/meta", tags=["meta"])
def page(model, db, skip, limit):
    query = db.query(model).filter_by(is_active=True)
    return success({"items": serialize(query.offset(skip).limit(limit).all()), "total": query.count(), "limit": limit, "skip": skip})
@meta.get("/skills")
def meta_skills(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), user=Depends(get_current_user), db=Depends(get_db)): return page(Skill, db, skip, limit)
@meta.get("/career-roles")
def meta_roles(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), user=Depends(get_current_user), db=Depends(get_db)): return page(CareerRole, db, skip, limit)
router.include_router(meta)
