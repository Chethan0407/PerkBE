from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.sheet import (
    Company, CompanyCreate, Platform, PlatformCreate,
    Sheet, SheetCreate, SheetUpdate, Row, RowCreate, RowUpdate
)
from app.services.sheet_service import (
    create_company, get_company, get_companies,
    create_platform, get_platform, get_platforms,
    create_sheet, get_sheet, get_sheets, update_sheet, delete_sheet,
    create_row, get_row, get_rows, update_row, delete_row,
    get_company_sheets
)
from pydantic import BaseModel

router = APIRouter()

class DetailedSheet(BaseModel):
    id: str
    name: str
    company_id: int
    platform_id: int
    sheet_type: str
    description: Optional[str]
    is_template: bool
    created_at: str
    updated_at: str
    rows: List[Dict[str, Any]]

class CompleteSheet(BaseModel):
    id: str
    name: str
    company_id: int
    platform_id: int
    sheet_type: str
    description: Optional[str]
    is_template: bool
    created_at: str
    updated_at: str
    columns: List[str]
    headers: List[str]
    rows: List[Dict[str, Any]]

# Company endpoints
@router.post("/companies", response_model=Company)
def create_new_company(company: CompanyCreate, db: Session = Depends(get_db)):
    return create_company(db=db, company=company)

@router.get("/companies", response_model=List[Company])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_companies(db, skip=skip, limit=limit)

@router.get("/companies/{company_id}", response_model=Company)
def read_company(company_id: int, db: Session = Depends(get_db)):
    db_company = get_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

# Platform endpoints
@router.post("/platforms", response_model=Platform)
def create_new_platform(platform: PlatformCreate, db: Session = Depends(get_db)):
    return create_platform(db=db, platform=platform)

@router.get("/platforms", response_model=List[Platform])
def read_platforms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_platforms(db, skip=skip, limit=limit)

@router.get("/platforms/{platform_id}", response_model=Platform)
def read_platform(platform_id: int, db: Session = Depends(get_db)):
    db_platform = get_platform(db, platform_id=platform_id)
    if db_platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")
    return db_platform

# Sheet endpoints
@router.post("/sheets", response_model=Sheet)
def create_new_sheet(sheet: SheetCreate, db: Session = Depends(get_db)):
    return create_sheet(db=db, sheet=sheet)

@router.get("/sheets", response_model=List[Sheet])
def read_sheets(
    company_id: Optional[int] = None,
    platform_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_sheets(db, company_id=company_id, platform_id=platform_id, skip=skip, limit=limit)

@router.get("/sheets/{sheet_id}", response_model=Sheet)
def read_sheet(sheet_id: int, db: Session = Depends(get_db)):
    db_sheet = get_sheet(db, sheet_id=sheet_id)
    if db_sheet is None:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return db_sheet

@router.put("/sheets/{sheet_id}", response_model=Sheet)
def update_sheet_endpoint(sheet_id: int, sheet: SheetUpdate, db: Session = Depends(get_db)):
    db_sheet = update_sheet(db, sheet_id=sheet_id, sheet=sheet)
    if db_sheet is None:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return db_sheet

@router.delete("/sheets/{sheet_id}")
def delete_sheet_endpoint(sheet_id: int, db: Session = Depends(get_db)):
    if not delete_sheet(db, sheet_id=sheet_id):
        raise HTTPException(status_code=404, detail="Sheet not found")
    return {"message": "Sheet deleted successfully"}

# Row endpoints
@router.post("/sheets/{sheet_id}/rows", response_model=Row)
def create_new_row(sheet_id: int, row: RowCreate, db: Session = Depends(get_db)):
    return create_row(db=db, sheet_id=sheet_id, row=row)

@router.get("/sheets/{sheet_id}/rows", response_model=List[Row])
def read_rows(sheet_id: int, db: Session = Depends(get_db)):
    return get_rows(db, sheet_id=sheet_id)

@router.get("/rows/{row_id}", response_model=Row)
def read_row(row_id: int, db: Session = Depends(get_db)):
    db_row = get_row(db, row_id=row_id)
    if db_row is None:
        raise HTTPException(status_code=404, detail="Row not found")
    return db_row

@router.put("/rows/{row_id}", response_model=Row)
def update_row_endpoint(row_id: int, row: RowUpdate, db: Session = Depends(get_db)):
    db_row = update_row(db, row_id=row_id, row=row)
    if db_row is None:
        raise HTTPException(status_code=404, detail="Row not found")
    return db_row

@router.delete("/rows/{row_id}")
def delete_row_endpoint(row_id: int, db: Session = Depends(get_db)):
    if not delete_row(db, row_id=row_id):
        raise HTTPException(status_code=404, detail="Row not found")
    return {"message": "Row deleted successfully"}

# Company sheets endpoint
@router.get("/companies/{company_id}/sheets", response_model=List[Sheet])
def read_company_sheets(
    company_id: int,
    platform_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_company_sheets(db, company_id=company_id, platform_id=platform_id)

@router.get("/sheets/{sheet_id}/detailed", response_model=DetailedSheet)
def get_detailed_sheet(sheet_id: str, db: Session = Depends(get_db)):
    db_sheet = get_sheet(db, sheet_id=sheet_id)
    if db_sheet is None:
        raise HTTPException(status_code=404, detail="Sheet not found")
    
    rows = get_rows(db, sheet_id=sheet_id)
    
    return {
        "id": str(db_sheet.id),
        "name": db_sheet.name,
        "company_id": db_sheet.company_id,
        "platform_id": db_sheet.platform_id,
        "sheet_type": db_sheet.sheet_type,
        "description": db_sheet.description,
        "is_template": db_sheet.is_template,
        "created_at": db_sheet.created_at.isoformat(),
        "updated_at": db_sheet.updated_at.isoformat() if db_sheet.updated_at else None,
        "rows": [{"row_number": row.row_number, "data": row.data} for row in rows]
    }

@router.get("/sheets/{sheet_id}/complete", response_model=CompleteSheet)
def get_complete_sheet(sheet_id: str, db: Session = Depends(get_db)):
    db_sheet = get_sheet(db, sheet_id=sheet_id)
    if db_sheet is None:
        raise HTTPException(status_code=404, detail="Sheet not found")
    
    rows = get_rows(db, sheet_id=sheet_id)
    
    # Get all unique column names from the data
    columns = set()
    for row in rows:
        if row.data:
            columns.update(row.data.keys())
    
    # Convert columns to list and sort them
    columns_list = sorted(list(columns))
    
    # Use the same columns as headers for now
    headers = columns_list
    
    return {
        "id": str(db_sheet.id),
        "name": db_sheet.name,
        "company_id": db_sheet.company_id,
        "platform_id": db_sheet.platform_id,
        "sheet_type": db_sheet.sheet_type,
        "description": db_sheet.description,
        "is_template": db_sheet.is_template,
        "created_at": db_sheet.created_at.isoformat(),
        "updated_at": db_sheet.updated_at.isoformat() if db_sheet.updated_at else None,
        "columns": columns_list,
        "headers": headers,
        "rows": [{"row_number": row.row_number, "data": row.data} for row in rows]
    } 