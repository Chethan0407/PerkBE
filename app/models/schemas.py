from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class TestCase(BaseModel):
    id: str
    title: str
    status: str

class UserInfo(BaseModel):
    email: str
    role: str

class SheetAccess(BaseModel):
    sheet_id: str
    name: str
    permission_level: str  # "read" or "write"

class UserSheets(BaseModel):
    user_id: str
    sheets: List[SheetAccess]

class SheetOperation(BaseModel):
    operation: str  # "read", "write", "update", "delete"
    data: Dict
    range: Optional[str]

class SheetResponse(BaseModel):
    data: List[dict]
    status: str
    message: Optional[str]

class ReleasePlanBase(BaseModel):
    title: str
    description: str
    release_date: datetime
    status: str  # "Draft", "In Review", "Approved", "Completed"
    version: str
    owner_id: int

class ReleasePlanCreate(ReleasePlanBase):
    pass

class ReleasePlanUpdate(ReleasePlanBase):
    title: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    status: Optional[str] = None
    version: Optional[str] = None

class ReleasePlan(ReleasePlanBase):
    id: int
    created_at: datetime
    updated_at: datetime
    documents: List[str] = []
    comments: List[str] = []

    class Config:
        orm_mode = True

class CommentCreate(BaseModel):
    content: str
    user_id: int

class Comment(CommentCreate):
    id: int
    created_at: datetime
    plan_id: int 