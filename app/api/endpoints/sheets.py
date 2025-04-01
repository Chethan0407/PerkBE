from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ...services.sheets import SheetsService
from ...core.config import settings
from typing import List
from pydantic import BaseModel
import asyncio

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class CellUpdate(BaseModel):
    range: str
    value: str

class NewSheet(BaseModel):
    title: str

# Android Endpoints
@router.get("/android/list/{sheet_id}")
async def get_android_sheets(sheet_id: str):
    """Get all sheets in Android spreadsheet"""
    return await SheetsService.get_all_sheets(sheet_id)

@router.get("/android/data/{sheet_id}")
async def get_android_sheet_data(sheet_id: str, sheet_name: str = None):
    """Get data from Android sheet"""
    return await SheetsService.get_sheet_data(sheet_id, sheet_name)

@router.get("/android/view/{sheet_id}")
async def view_android_sheet(request: Request, sheet_id: str):
    """View Android sheet in HTML format"""
    try:
        sheets = await SheetsService.get_all_sheets(sheet_id)
        sheet_data = await SheetsService.get_sheet_data(sheet_id)
        
        return templates.TemplateResponse(
            "sheet_view.html",
            {
                "request": request, 
                "data": sheet_data["data"],
                "sheets": sheets["sheets"],
                "platform": "Android",
                "sheet_id": sheet_id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# iOS Endpoints
@router.get("/ios/list/{sheet_id}")
async def get_ios_sheets(sheet_id: str):
    """Get all sheets in iOS spreadsheet"""
    return await SheetsService.get_all_sheets(sheet_id)

@router.get("/ios/data/{sheet_id}")
async def get_ios_sheet_data(sheet_id: str, sheet_name: str = None):
    """Get data from iOS sheet"""
    return await SheetsService.get_sheet_data(sheet_id, sheet_name)

@router.get("/ios/view/{sheet_id}")
async def view_ios_sheet(request: Request, sheet_id: str):
    """View iOS sheet in HTML format"""
    try:
        sheets = await SheetsService.get_all_sheets(sheet_id)
        all_sheets_data = {}
        
        # Get data from all sheets
        for sheet_name in sheets["sheets"]:
            sheet_data = await SheetsService.get_sheet_data(sheet_id, sheet_name)
            all_sheets_data[sheet_name] = sheet_data["data"]
        
        return templates.TemplateResponse(
            "sheet_view.html",
            {
                "request": request, 
                "all_data": all_sheets_data,
                "sheets": sheets["sheets"],
                "platform": "iOS",
                "sheet_id": sheet_id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Common operations with platform-specific routes
@router.post("/{platform}/{sheet_id}/cell")
async def update_cell(platform: str, sheet_id: str, update: CellUpdate):
    """Update a single cell"""
    return await SheetsService.update_cell(sheet_id, update.range, update.value)

@router.post("/{platform}/{sheet_id}/row")
async def add_row(platform: str, sheet_id: str, values: List[str]):
    """Add a new row"""
    return await SheetsService.append_row(sheet_id, values)

@router.delete("/{platform}/{sheet_id}/row/{row_number}")
async def delete_row(platform: str, sheet_id: str, row_number: int):
    """Delete a row"""
    return await SheetsService.delete_row(sheet_id, row_number)

@router.post("/{platform}/{sheet_id}/new-sheet")
async def create_new_sheet(platform: str, sheet_id: str, sheet_info: NewSheet):
    """Create a new sheet"""
    result = await SheetsService.create_new_sheet(sheet_id, sheet_info.title)
    if result["status"] == "success":
        return RedirectResponse(
            url=f"/api/v1/sheets/{platform}/view/{sheet_id}?new_sheet={sheet_info.title}",
            status_code=303
        )
    return result

@router.get("/view/{sheet_id}")
async def redirect_to_android(sheet_id: str):
    """Redirect old URLs to Android view"""
    return RedirectResponse(url=f"/api/v1/sheets/android/view/{sheet_id}")

@router.post("/{platform}/{sheet_id}/rename")
async def rename_sheet(platform: str, sheet_id: str, data: dict):
    """Rename a sheet"""
    return await SheetsService.rename_sheet(sheet_id, data["old_name"], data["new_name"])

@router.post("/{platform}/{sheet_id}/duplicate")
async def duplicate_sheet(platform: str, sheet_id: str, data: dict):
    """Duplicate a sheet"""
    return await SheetsService.duplicate_sheet(sheet_id, data["source_name"], data["new_name"])

@router.delete("/{platform}/{sheet_id}/sheet/{sheet_name}")
async def delete_sheet(platform: str, sheet_id: str, sheet_name: str):
    """Delete a sheet"""
    return await SheetsService.delete_sheet(sheet_id, sheet_name)

@router.post("/{platform}/{sheet_id}/format")
async def format_cell(platform: str, sheet_id: str, format_data: dict):
    """Update cell formatting"""
    return await SheetsService.format_cell(sheet_id, format_data["range"], format_data["format"]) 