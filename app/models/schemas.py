from pydantic import BaseModel
from typing import List, Dict, Optional

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