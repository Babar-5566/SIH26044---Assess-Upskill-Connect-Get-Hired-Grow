from pathlib import Path
from uuid import uuid4
from app.core.config import settings
def save_resume(file,student_id):
 filename = file.filename or "resume"
 ext=filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
 if ext not in ('pdf','doc','docx'): raise ValueError('extension')
 data=file.file.read()
 if len(data)>settings.max_resume_size_mb*1024*1024: raise ValueError('size')
 d=Path(settings.upload_dir)/'resumes'/str(student_id); d.mkdir(parents=True,exist_ok=True); path=d/f'{uuid4()}.{ext}'; path.write_bytes(data); return path,len(data)
