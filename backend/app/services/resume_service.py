import re
from io import BytesIO
from pathlib import PurePath
from zipfile import BadZipFile, ZipFile
from app.core.config import settings

MIME_TYPES = {
 "pdf": "application/pdf",
 "doc": "application/msword",
 "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

def _validate_content(data: bytes, ext: str) -> None:
 if not data: raise ValueError('empty')
 if ext == 'pdf' and not data.startswith(b'%PDF-'): raise ValueError('content')
 if ext == 'doc' and not data.startswith(bytes.fromhex('D0CF11E0A1B11AE1')): raise ValueError('content')
 if ext == 'docx':
  try:
   with ZipFile(BytesIO(data)) as archive:
    names = set(archive.namelist())
    if '[Content_Types].xml' not in names or 'word/document.xml' not in names: raise ValueError('content')
  except BadZipFile as exc: raise ValueError('content') from exc

def read_resume(file):
 filename = PurePath(file.filename or "resume").name
 filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename)[:255] or "resume"
 ext=filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
 if ext not in ('pdf','doc','docx'): raise ValueError('extension')
 max_bytes = settings.max_resume_size_mb * 1024 * 1024
 data=file.file.read(max_bytes + 1)
 if len(data) > max_bytes: raise ValueError('size')
 _validate_content(data, ext)
 claimed_mime = (file.content_type or '').lower().split(';', 1)[0].strip()
 if claimed_mime and claimed_mime != 'application/octet-stream' and claimed_mime != MIME_TYPES[ext]: raise ValueError('mime')
 return data, len(data), ext, filename, MIME_TYPES[ext]
