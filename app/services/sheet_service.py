from sqlalchemy.orm import Session
from app.models.database import Company, Platform, Sheet, Row
from app.schemas.sheet import (
    CompanyCreate, PlatformCreate, SheetCreate, SheetUpdate,
    RowCreate, RowUpdate
)
from typing import List, Optional, Dict, Any
from datetime import datetime

# Company operations
def create_company(db: Session, company: CompanyCreate) -> Company:
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_company(db: Session, company_id: int) -> Optional[Company]:
    return db.query(Company).filter(Company.id == company_id).first()

def get_companies(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
    return db.query(Company).offset(skip).limit(limit).all()

# Platform operations
def create_platform(db: Session, platform: PlatformCreate) -> Platform:
    db_platform = Platform(**platform.dict())
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    return db_platform

def get_platform(db: Session, platform_id: int) -> Optional[Platform]:
    return db.query(Platform).filter(Platform.id == platform_id).first()

def get_platforms(db: Session, skip: int = 0, limit: int = 100) -> List[Platform]:
    return db.query(Platform).offset(skip).limit(limit).all()

# Sheet operations
def create_sheet(db: Session, sheet: SheetCreate) -> Sheet:
    db_sheet = Sheet(**sheet.dict())
    db.add(db_sheet)
    db.commit()
    db.refresh(db_sheet)
    return db_sheet

def get_sheet(db: Session, sheet_id: int) -> Optional[Sheet]:
    return db.query(Sheet).filter(Sheet.id == sheet_id).first()

def get_sheets(
    db: Session,
    company_id: Optional[int] = None,
    platform_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Sheet]:
    query = db.query(Sheet)
    if company_id:
        query = query.filter(Sheet.company_id == company_id)
    if platform_id:
        query = query.filter(Sheet.platform_id == platform_id)
    return query.offset(skip).limit(limit).all()

def update_sheet(db: Session, sheet_id: int, sheet: SheetUpdate) -> Optional[Sheet]:
    db_sheet = get_sheet(db, sheet_id)
    if db_sheet:
        update_data = sheet.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_sheet, key, value)
        db.commit()
        db.refresh(db_sheet)
    return db_sheet

def delete_sheet(db: Session, sheet_id: int) -> bool:
    db_sheet = get_sheet(db, sheet_id)
    if db_sheet:
        db.delete(db_sheet)
        db.commit()
        return True
    return False

# Row operations
def create_row(db: Session, sheet_id: int, row: RowCreate) -> Row:
    db_row = Row(**row.dict(), sheet_id=sheet_id)
    db.add(db_row)
    db.commit()
    db.refresh(db_row)
    return db_row

def get_row(db: Session, row_id: int) -> Optional[Row]:
    return db.query(Row).filter(Row.id == row_id).first()

def get_rows(db: Session, sheet_id: int) -> List[Row]:
    return db.query(Row).filter(Row.sheet_id == sheet_id).order_by(Row.row_number).all()

def update_row(db: Session, row_id: int, row: RowUpdate) -> Optional[Row]:
    db_row = get_row(db, row_id)
    if db_row:
        update_data = row.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_row, key, value)
        db.commit()
        db.refresh(db_row)
    return db_row

def delete_row(db: Session, row_id: int) -> bool:
    db_row = get_row(db, row_id)
    if db_row:
        db.delete(db_row)
        db.commit()
        return True
    return False

def get_company_sheets(
    db: Session,
    company_id: int,
    platform_id: Optional[int] = None
) -> List[Sheet]:
    query = db.query(Sheet).filter(Sheet.company_id == company_id)
    if platform_id:
        query = query.filter(Sheet.platform_id == platform_id)
    return query.all() 