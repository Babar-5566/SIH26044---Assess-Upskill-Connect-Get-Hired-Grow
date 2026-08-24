from pydantic import BaseModel
class DocumentOut(BaseModel): id:str; file_name:str; file_size:int; mime_type:str|None; is_active:bool
