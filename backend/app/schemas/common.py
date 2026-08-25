from pydantic import BaseModel, ConfigDict
class Out(BaseModel): model_config=ConfigDict(from_attributes=True)
class Page(BaseModel): items:list; total:int; limit:int; skip:int
