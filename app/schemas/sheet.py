from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class CompanyBase(BaseModel):
    name: str

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PlatformBase(BaseModel):
    name: str

class PlatformCreate(PlatformBase):
    pass

class Platform(PlatformBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RowBase(BaseModel):
    row_number: int
    data: Dict[str, Any]

class RowCreate(RowBase):
    pass

class RowUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None

class Row(RowBase):
    id: int
    sheet_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SheetBase(BaseModel):
    name: str
    company_id: int
    platform_id: int
    sheet_type: str
    description: Optional[str] = None
    is_template: bool = False

class SheetCreate(SheetBase):
    pass

class SheetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sheet_type: Optional[str] = None
    is_template: Optional[bool] = None

class Sheet(SheetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    company: Company
    platform: Platform
    rows: List[Row] = []

    class Config:
        from_attributes = True 