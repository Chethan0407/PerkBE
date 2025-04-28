from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class CompanyBase(BaseModel):
    name: str

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PlatformResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SheetBase(BaseModel):
    title: str
    company_id: str
    platform_id: str
    sheet_type: str
    data: Optional[List[List[str]]] = None

class SheetCreate(SheetBase):
    pass

class SheetUpdate(BaseModel):
    range: str
    values: List[List[str]]

class SheetResponse(SheetBase):
    id: str
    created_at: datetime
    updated_at: datetime
    company: CompanyResponse
    platform: PlatformResponse

    class Config:
        from_attributes = True

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