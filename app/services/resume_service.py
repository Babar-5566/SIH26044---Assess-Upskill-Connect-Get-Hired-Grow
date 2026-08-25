import re
from pathlib import PurePath
from app.core.config import settings
def read_resume(file):
 filename = PurePath(file.filename or "resume").name
 filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename)[:255] or "resume"
 ext=filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
 if ext not in ('pdf','doc','docx'): raise ValueError('extension')
 max_bytes = settings.max_resume_size_mb * 1024 * 1024
 data=file.file.read(max_bytes + 1)
 if len(data) > max_bytes: raise ValueError('size')
 return data, len(data), ext, filename
