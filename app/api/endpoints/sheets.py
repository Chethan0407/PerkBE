from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ...services.sheets import SheetsService
from ...models.database import Sheet
from ...db.session import get_db
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
    platform: str  # android, ios, web, api

@router.post("/create")
async def create_sheet(sheet_info: NewSheet):
    """Create a new sheet with our own ID system"""
    db = next(get_db())
    sheet = Sheet(
        title=sheet_info.title,
        platform=sheet_info.platform,
        data=[],  # Initialize with empty data
        sheets=["Sheet1"]  # Initialize with default sheet
    )
    db.add(sheet)
    db.commit()
    db.refresh(sheet)
    
    return {
        "status": "success",
        "sheet_id": sheet.id,
        "title": sheet.title,
        "platform": sheet.platform
    }

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
@router.get("/ios/data/{sheet_id}")
async def get_ios_sheet_data(sheet_id: str, sheet_name: str = None):
    """Get iOS sheet data"""
    try:
        return await SheetsService.get_sheet_data(sheet_id, sheet_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/ios/list/{sheet_id}")
async def get_ios_sheets(sheet_id: str):
    """Get all sheets in iOS spreadsheet"""
    try:
        return await SheetsService.get_all_sheets(sheet_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/ios/{sheet_id}/cell")
async def update_ios_cell(sheet_id: str, cell_data: CellUpdate):
    """Update iOS sheet cell"""
    try:
        return await SheetsService.update_cell(sheet_id, cell_data.range, cell_data.value)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ios/{sheet_id}/row")
async def add_ios_row(sheet_id: str, values: List[str]):
    """Add a new row to iOS sheet"""
    try:
        return await SheetsService.append_row(sheet_id, values)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/ios/{sheet_id}/row/{row_number}")
async def delete_ios_row(sheet_id: str, row_number: int):
    """Delete a row from iOS sheet"""
    try:
        return await SheetsService.delete_row(sheet_id, row_number)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ios/{sheet_id}/new-sheet")
async def create_ios_sheet(sheet_id: str, sheet_info: NewSheet):
    """Create a new iOS sheet"""
    try:
        return await SheetsService.create_new_sheet(sheet_id, sheet_info.title)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/ios/{sheet_id}/sheet/{sheet_name}")
async def delete_ios_sheet(sheet_id: str, sheet_name: str):
    """Delete an iOS sheet"""
    try:
        return await SheetsService.delete_sheet(sheet_id, sheet_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ios/{sheet_id}/rename")
async def rename_ios_sheet(sheet_id: str, data: dict):
    """Rename an iOS sheet"""
    try:
        return await SheetsService.rename_sheet(
            sheet_id, 
            data["old_name"], 
            data["new_name"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ios/{sheet_id}/duplicate")
async def duplicate_ios_sheet(sheet_id: str, data: dict):
    """Duplicate an iOS sheet"""
    try:
        return await SheetsService.duplicate_sheet(
            sheet_id,
            data["source_name"],
            data["new_name"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ios/{sheet_id}/format")
async def format_ios_cell(sheet_id: str, format_data: dict):
    """Update iOS cell formatting"""
    try:
        return await SheetsService.format_cell(
            sheet_id,
            format_data["range"],
            format_data["format"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# API Testing Endpoints
@router.get("/api/data/{sheet_id}")
async def get_api_sheet_data(sheet_id: str, sheet_name: str = None):
    """Get API testing sheet data"""
    return await SheetsService.get_sheet_data(sheet_id, sheet_name)

@router.post("/api/{sheet_id}/cell")
async def update_api_cell(sheet_id: str, cell_data: dict):
    """Update API sheet cell"""
    return await SheetsService.update_cell(sheet_id, cell_data["range"], cell_data["value"])

@router.post("/api/{sheet_id}/new-sheet")
async def create_api_sheet(sheet_id: str, data: dict):
    """Create new API sheet"""
    return await SheetsService.create_sheet(sheet_id, data["title"])

@router.delete("/api/{sheet_id}/sheet/{sheet_name}")
async def delete_api_sheet(sheet_id: str, sheet_name: str):
    """Delete API sheet"""
    return await SheetsService.delete_sheet(sheet_id, sheet_name)

# Web Testing Endpoints
@router.get("/web/data/{sheet_id}")
async def get_web_sheet_data(sheet_id: str, sheet_name: str = None):
    """Get web testing sheet data"""
    return await SheetsService.get_sheet_data(sheet_id, sheet_name)

@router.post("/web/{sheet_id}/cell")
async def update_web_cell(sheet_id: str, cell_data: dict):
    """Update web sheet cell"""
    return await SheetsService.update_cell(sheet_id, cell_data["range"], cell_data["value"])

@router.post("/web/{sheet_id}/new-sheet")
async def create_web_sheet(sheet_id: str, data: dict):
    """Create new web sheet"""
    return await SheetsService.create_sheet(sheet_id, data["title"])

@router.delete("/web/{sheet_id}/sheet/{sheet_name}")
async def delete_web_sheet(sheet_id: str, sheet_name: str):
    """Delete web sheet"""
    return await SheetsService.delete_sheet(sheet_id, sheet_name)

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

@router.get("/")
async def sheet_home(request: Request):
    """Landing page to select platform"""
    return templates.TemplateResponse(
        "platform_select.html",
        {
            "request": request,
            "platforms": [
                {
                    "name": "Android Testing",
                    "url": "/api/v1/sheets/android/view/",
                    "icon": "📱"
                },
                {
                    "name": "iOS Testing",
                    "url": "/api/v1/sheets/ios/view/",
                    "icon": "📱"
                },
                {
                    "name": "API Testing",
                    "url": "/api/v1/sheets/api/view/",
                    "icon": "🔌"
                },
                {
                    "name": "Web Testing",
                    "url": "/api/v1/sheets/web/view/",
                    "icon": "🌐"
                }
            ]
        }
    )

@router.get("/{platform}/view/{sheet_id}")
async def view_sheet(platform: str, sheet_id: str, request: Request):
    """View sheet based on platform"""
    try:
        sheets = await SheetsService.get_all_sheets(sheet_id)
        sheet_data = await SheetsService.get_sheet_data(sheet_id)
        
        return templates.TemplateResponse(
            "sheet_view.html",
            {
                "request": request,
                "data": sheet_data["data"],
                "sheets": sheets["sheets"],
                "platform": platform.capitalize(),
                "sheet_id": sheet_id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 