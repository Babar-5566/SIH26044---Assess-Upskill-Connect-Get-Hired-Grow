from app.models import AuditLog
def log(db,user_id,action,entity=None,entity_id=None,details=None,ip=None):
 db.add(AuditLog(user_id=user_id,action=action,entity=entity,entity_id=entity_id,details=details,ip=ip)); db.commit()
