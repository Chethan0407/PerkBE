from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.database import Sheet, Company, Platform
from ..core.config import settings
import uuid
from datetime import datetime
from fastapi import HTTPException
from ..db.session import get_db

class SheetsService:
    @staticmethod
    async def verify_sheet_access(sheet_id: str, user_id: str) -> bool:
        db = next(get_db())
        sheet = db.query(Sheet).filter(Sheet.id == sheet_id).first()
        return sheet is not None

    @staticmethod
    async def get_sheet_data(sheet_id: str, sheet_name: str = None):
        """Get data from a specific sheet including empty cells"""
        db = next(get_db())
        sheet = db.query(Sheet).filter(Sheet.id == sheet_id).first()
        
        if not sheet:
            raise HTTPException(status_code=404, detail="Sheet not found")
            
        headers = [
            "Test Case ID",
            "Module",
            "Test Case",
            "Expected Outcome",
            "Actual Outcome",
            "Priority",
            "Assigned To",
            "Status",
            "Execution Date",
            "Test Result",
            "Comments"
        ]
        
        # Initialize data if it's empty
        if not sheet.data:
            sheet.data = [headers]
            db.commit()
            
        return {"data": sheet.data}

    @staticmethod
    async def append_data(sheet_id: str, data: List[List[str]]):
        """Append new rows to the sheet"""
        db = next(get_db())
        sheet = db.query(Sheet).filter(Sheet.id == sheet_id).first()
        
        if not sheet:
            raise HTTPException(status_code=404, detail="Sheet not found")
            
        # Initialize data if empty
        if not sheet.data:
            headers = [
                "Test Case ID", "Module", "Test Case", "Expected Outcome",
                "Actual Outcome", "Priority", "Assigned To", "Status",
                "Execution Date", "Test Result", "Comments"
            ]
            sheet.data = [headers]
        
        # Append each row, ensuring it has the same number of columns as headers
        for row in data:
            # Pad or truncate the row to match header length
            padded_row = (row + [""] * len(sheet.data[0]))[:len(sheet.data[0])]
            sheet.data.append(padded_row)
            
        db.commit()
        return {"status": "success", "updated": len(data)}

    @staticmethod
    async def update_data(sheet_id: str, range: str, data: List[List[str]]):
        """Update specific cells"""
        db = next(get_db())
        sheet = db.query(Sheet).filter(Sheet.id == sheet_id).first()
        
        if not sheet:
            raise HTTPException(status_code=404, detail="Sheet not found")
            
        # Parse range (e.g., "A1:B2")
        start_col, start_row = SheetsService._parse_range(range)
        
        # Ensure data is initialized
        if not sheet.data:
            headers = [
                "Test Case ID", "Module", "Test Case", "Expected Outcome",
                "Actual Outcome", "Priority", "Assigned To", "Status",
                "Execution Date", "Test Result", "Comments"
            ]
            sheet.data = [headers]
        
        # Ensure we have enough rows
        while len(sheet.data) <= start_row:
            sheet.data.append([""] * len(sheet.data[0]))
        
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                row_idx = start_row + i
                col_idx = start_col + j
                
                # Ensure we have enough columns in this row
                while len(sheet.data[row_idx]) <= col_idx:
                    sheet.data[row_idx].append("")
                
                sheet.data[row_idx][col_idx] = value
                    
        db.commit()
        return {"status": "success", "updated": len(data) * len(data[0])}

    @staticmethod
    def _parse_range(range_str: str) -> tuple:
        """Parse Excel-style range into column and row indices"""
        col = ord(range_str[0].upper()) - ord('A')
        row = int(range_str[1:]) - 1
        return col, row

    @staticmethod
    async def clear_range(sheet_id: str, range: str):
        """Clear data in specified range"""
        db = next(get_db())
        sheet = db.query(Sheet).filter(Sheet.id == sheet_id).first()
        
        if not sheet:
            raise HTTPException(status_code=404, detail="Sheet not found")
            
        start_col, start_row = SheetsService._parse_range(range)
        end_col, end_row = SheetsService._parse_range(range.split(':')[1])
        
        for i in range(start_row, end_row + 1):
            for j in range(start_col, end_col + 1):
                if i < len(sheet.data) and j < len(sheet.data[i]):
                    sheet.data[i][j] = ""
                    
        db.commit()
        return {"status": "success", "cleared": (end_row - start_row + 1) * (end_col - start_col + 1)}

    @staticmethod
    async def update_cell(sheet_id: str, cell_range: str, value: str):
        """Update a single cell"""
        return await SheetsService.update_data(sheet_id, cell_range, [[value]])

    @staticmethod
    async def append_row(sheet_id: str, values: List[str]):
        """Add a new row"""
        return await SheetsService.append_data(sheet_id, [values])

    @staticmethod
    async def delete_row(sheet_id: str, row_number: int):
        """Delete a row"""
        db = next(get_db())
        sheet = db.query(Sheet).filter(Sheet.id == sheet_id).first()
        
        if not sheet:
            raise HTTPException(status_code=404, detail="Sheet not found")
            
        if 0 <= row_number - 1 < len(sheet.data):
            del sheet.data[row_number - 1]
            db.commit()
            return {"status": "success", "result": "Row deleted"}
        else:
            raise HTTPException(status_code=400, detail="Invalid row number")

    @staticmethod
    async def get_all_sheets(sheet_id: str):
        """Get all sheets in the spreadsheet"""
        db = next(get_db())
        sheet = db.query(Sheet).filter(Sheet.id == sheet_id).first()
        
        if not sheet:
            raise HTTPException(status_code=404, detail="Sheet not found")
            
        return {"sheets": sheet.sheets}

    @staticmethod
    async def create_new_sheet(sheet_id: str, title: str):
        """Create a new empty sheet with test case management columns"""
        db = next(get_db())
        sheet = db.query(Sheet).filter(Sheet.id == sheet_id).first()
        
        if not sheet:
            raise HTTPException(status_code=404, detail="Sheet not found")
            
        # Generate next available sheet name
        base_title = "Sheet"
        counter = 1
        while f"{base_title}{counter}" in sheet.sheets:
            counter += 1
        title = f"{base_title}{counter}"
        
        # Add new sheet to sheets list
        sheet.sheets.append(title)
        db.commit()
        
        return {"status": "success", "title": title}

    @staticmethod
    async def delete_sheet(sheet_id: str, sheet_name: str):
        """Delete a sheet"""
        db = next(get_db())
        sheet = db.query(Sheet).filter(Sheet.id == sheet_id).first()
        
        if not sheet:
            raise HTTPException(status_code=404, detail="Sheet not found")
            
        if sheet_name in sheet.sheets:
            sheet.sheets.remove(sheet_name)
            db.commit()
            return {"status": "success", "result": "Sheet deleted"}
        else:
            raise HTTPException(status_code=400, detail="Sheet not found")

    @staticmethod
    async def rename_sheet(sheet_id: str, old_name: str, new_name: str):
        """Rename a sheet"""
        db = next(get_db())
        sheet = db.query(Sheet).filter(Sheet.id == sheet_id).first()
        
        if not sheet:
            raise HTTPException(status_code=404, detail="Sheet not found")
            
        if old_name in sheet.sheets:
            index = sheet.sheets.index(old_name)
            sheet.sheets[index] = new_name
            db.commit()
            return {"status": "success", "result": "Sheet renamed"}
        else:
            raise HTTPException(status_code=400, detail="Sheet not found")

    @staticmethod
    async def duplicate_sheet(sheet_id: str, source_name: str, new_name: str):
        """Duplicate a sheet"""
        db = next(get_db())
        sheet = db.query(Sheet).filter(Sheet.id == sheet_id).first()
        
        if not sheet:
            raise HTTPException(status_code=404, detail="Sheet not found")
            
        if source_name in sheet.sheets:
            sheet.sheets.append(new_name)
            db.commit()
            return {"status": "success", "result": "Sheet duplicated"}
        else:
            raise HTTPException(status_code=400, detail="Source sheet not found")

    @staticmethod
    async def format_cell(sheet_id: str, cell_range: str, format_data: dict):
        """Update cell formatting"""
        # Formatting is not supported in our simple implementation
        return {"status": "success", "result": "Formatting not supported"}

    @staticmethod
    async def create_sheet(
        db: Session,
        title: str,
        company_id: str,
        platform_id: str,
        sheet_type: str,
        data: Optional[List[List[Any]]] = None
    ) -> Sheet:
        """Create a new sheet for a company and platform"""
        sheet = Sheet(
            title=title,
            company_id=company_id,
            platform_id=platform_id,
            sheet_type=sheet_type,
            data=data or [],
            sheets=["Sheet1"]  # Default sheet name
        )
        db.add(sheet)
        db.commit()
        db.refresh(sheet)
        return sheet

    @staticmethod
    async def get_sheets(
        db: Session,
        company_id: Optional[str] = None,
        platform_id: Optional[str] = None,
        sheet_type: Optional[str] = None
    ) -> List[Sheet]:
        """Get sheets with optional filters"""
        query = db.query(Sheet)
        if company_id:
            query = query.filter(Sheet.company_id == company_id)
        if platform_id:
            query = query.filter(Sheet.platform_id == platform_id)
        if sheet_type:
            query = query.filter(Sheet.sheet_type == sheet_type)
        return query.all()

    @staticmethod
    async def get_sheet(db: Session, sheet_id: str) -> Optional[Sheet]:
        """Get a specific sheet by ID"""
        return db.query(Sheet).filter(Sheet.id == sheet_id).first()

    @staticmethod
    async def update_data(
        db: Session,
        sheet_id: str,
        range_str: str,
        values: List[List[Any]]
    ) -> Sheet:
        """Update sheet data in a specific range"""
        sheet = await SheetsService.get_sheet(db, sheet_id)
        if not sheet:
            raise ValueError("Sheet not found")

        # Parse range (e.g., "A1:B2")
        start_col, start_row = range_str[0], int(range_str[1:])
        
        # Ensure data exists
        if not sheet.data:
            sheet.data = []
        
        # Update data
        for i, row in enumerate(values):
            row_idx = start_row + i - 1
            if row_idx >= len(sheet.data):
                sheet.data.extend([[] for _ in range(row_idx - len(sheet.data) + 1)])
            
            for j, value in enumerate(row):
                col_idx = ord(range_str[0]) - ord('A') + j
                if col_idx >= len(sheet.data[row_idx]):
                    sheet.data[row_idx].extend([None] * (col_idx - len(sheet.data[row_idx]) + 1))
                sheet.data[row_idx][col_idx] = value

        sheet.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(sheet)
        return sheet

    @staticmethod
    async def append_data(
        db: Session,
        sheet_id: str,
        values: List[List[Any]],
        sheet_name: str = "Sheet1"
    ) -> Sheet:
        """Append data to a sheet"""
        sheet = await SheetsService.get_sheet(db, sheet_id)
        if not sheet:
            raise ValueError("Sheet not found")

        # Initialize data if empty
        if not sheet.data:
            sheet.data = []

        # Append new rows
        sheet.data.extend(values)
        sheet.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(sheet)
        return sheet

    @staticmethod
    async def create_company(db: Session, name: str) -> Company:
        """Create a new company"""
        company = Company(name=name)
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    async def get_companies(db: Session) -> List[Company]:
        """Get all companies"""
        return db.query(Company).all()

    @staticmethod
    async def get_platforms(db: Session) -> List[Platform]:
        """Get all platforms"""
        return db.query(Platform).all()

    @staticmethod
    async def get_company_sheets(
        db: Session,
        company_id: str,
        platform_id: Optional[str] = None
    ) -> List[Sheet]:
        """Get all sheets for a company, optionally filtered by platform"""
        query = db.query(Sheet).filter(Sheet.company_id == company_id)
        if platform_id:
            query = query.filter(Sheet.platform_id == platform_id)
        return query.all() 