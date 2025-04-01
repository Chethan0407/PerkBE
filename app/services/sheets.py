from typing import List, Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from ..core.config import settings
from ..models.schemas import SheetOperation
from fastapi import HTTPException

class SheetsService:
    @staticmethod
    async def verify_sheet_access(sheet_id: str, user_id: str) -> bool:
        # Verify if user has access to this sheet
        try:
            service = build('sheets', 'v4', credentials=settings.CREDENTIALS)
            sheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            return True
        except Exception:
            return False

    @staticmethod
    def _get_service():
        return build('sheets', 'v4', credentials=settings.CREDENTIALS)

    @staticmethod
    async def get_sheet_data(sheet_id: str, sheet_name: str = None):
        """Get data from a specific sheet including empty cells"""
        service = SheetsService._get_service()
        try:
            batch = service.spreadsheets().values().batchGet(
                spreadsheetId=sheet_id,
                ranges=[f"'{sheet_name}'!A1:M300" if sheet_name else "A1:M300"],
                majorDimension='ROWS',
                valueRenderOption='FORMATTED_VALUE'
            ).execute()

            values = batch.get('valueRanges', [{}])[0].get('values', [])
            
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
            
            if not values:
                values = [headers]
            
            # More efficient data formatting
            formatted_data = []
            header_len = len(headers)
            
            for row in values:
                # Use list comprehension for better performance
                padded_row = row + [''] * (header_len - len(row)) if len(row) < header_len else row
                formatted_data.append(dict(zip(headers, padded_row)))

            return {"data": formatted_data}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def append_data(sheet_id: str, data: List[List[str]]):
        """Append new rows to the sheet"""
        service = SheetsService._get_service()
        body = {
            'values': data
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range='A1',  # It will append after last row
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        return {"status": "success", "updated": result.get('updates')}

    @staticmethod
    async def update_data(sheet_id: str, range: str, data: List[List[str]]):
        """Update specific cells"""
        service = SheetsService._get_service()
        body = {
            'values': data
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        return {"status": "success", "updated": result.get('updatedCells')}

    @staticmethod
    async def clear_range(sheet_id: str, range: str):
        """Clear data in specified range"""
        service = SheetsService._get_service()
        result = service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range=range
        ).execute()
        return {"status": "success", "cleared": result.get('clearedRange')}

    @staticmethod
    async def update_sheet(sheet_id: str, operation: SheetOperation):
        service = SheetsService._get_service()
        
        if operation.operation == "write":
            body = {
                'values': operation.data.get('values', [])
            }
            result = service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=operation.range or 'A1',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
        elif operation.operation == "update":
            body = {
                'values': operation.data.get('values', [])
            }
            result = service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=operation.range,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
        return {"status": "success", "data": result}

    @staticmethod
    async def add_test_case(sheet_id: str, test_case: dict):
        try:
            client = gspread.authorize(settings.CREDENTIALS)
            sheet = client.open_by_key(sheet_id).sheet1
            sheet.append_row([test_case["id"], test_case["title"], test_case["status"]])
            return {"message": "Test case added successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_cell(sheet_id: str, cell_range: str, value: str):
        """Update a single cell"""
        service = SheetsService._get_service()
        body = {
            'values': [[value]]
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=cell_range,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        return {"status": "success", "updated": result.get('updatedCells')}

    @staticmethod
    async def append_row(sheet_id: str, values: List[str]):
        """Add a new row"""
        service = SheetsService._get_service()
        body = {
            'values': [values]
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range='A1',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        return {"status": "success", "updated": result.get('updates')}

    @staticmethod
    async def delete_row(sheet_id: str, row_number: int):
        """Delete a row"""
        service = SheetsService._get_service()
        request = {
            'requests': [{
                'deleteDimension': {
                    'range': {
                        'sheetId': 0,  # Assumes first sheet
                        'dimension': 'ROWS',
                        'startIndex': row_number - 1,
                        'endIndex': row_number
                    }
                }
            }]
        }
        result = service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=request
        ).execute()
        return {"status": "success", "result": result}

    @staticmethod
    async def get_all_sheets(sheet_id: str):
        """Get all sheets in the spreadsheet"""
        service = SheetsService._get_service()
        spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
        return {"sheets": sheets}

    @staticmethod
    async def create_new_sheet(sheet_id: str, title: str):
        """Create a new empty sheet with test case management columns"""
        service = SheetsService._get_service()
        try:
            # Get existing sheets to check name
            spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            existing_titles = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            
            # Generate next available sheet name
            base_title = "Sheet"
            counter = 1
            while f"{base_title}{counter}" in existing_titles:
                counter += 1
            title = f"{base_title}{counter}"
            
            # Create a fresh empty sheet with more columns
            request = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': title,
                            'gridProperties': {
                                'rowCount': 300,
                                'columnCount': 13,
                                'frozenRowCount': 1
                            },
                            'tabColor': {
                                'red': 0.8,
                                'green': 0.9,
                                'blue': 1.0
                            }
                        }
                    }
                }]
            }
            
            result = service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body=request
            ).execute()

            new_sheet_id = result['replies'][0]['addSheet']['properties']['sheetId']

            # Enhanced headers for test case management
            headers = [[
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
            ]]
            
            range_name = f"'{title}'!A1:M1"
            
            # Add headers
            body = {
                'values': headers
            }
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            # Format headers with Google Sheets style
            format_request = {
                'requests': [
                    {
                        'repeatCell': {
                            'range': {
                                'sheetId': new_sheet_id,
                                'startRowIndex': 0,
                                'endRowIndex': 1,
                                'startColumnIndex': 0,
                                'endColumnIndex': 13
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'backgroundColor': {
                                        'red': 0.95,
                                        'green': 0.95,
                                        'blue': 0.95
                                    },
                                    'textFormat': {
                                        'bold': True,
                                        'fontSize': 10
                                    },
                                    'verticalAlignment': 'MIDDLE',
                                    'horizontalAlignment': 'LEFT'
                                }
                            },
                            'fields': 'userEnteredFormat(backgroundColor,textFormat,verticalAlignment,horizontalAlignment)'
                        }
                    },
                    {
                        'autoResizeDimensions': {
                            'dimensions': {
                                'sheetId': new_sheet_id,
                                'dimension': 'COLUMNS',
                                'startIndex': 0,
                                'endIndex': 13
                            }
                        }
                    }
                ]
            }
            
            # Apply formatting
            service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body=format_request
            ).execute()

            return {
                "status": "success",
                "message": f"Sheet '{title}' created successfully",
                "sheet_name": title
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def delete_sheet(sheet_id: str, sheet_name: str):
        """Delete a sheet"""
        service = SheetsService._get_service()
        try:
            # Get all sheets to find the sheet ID
            spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            sheet_to_delete = None
            
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    sheet_to_delete = sheet['properties']['sheetId']
                    break
            
            if sheet_to_delete is None:
                raise HTTPException(status_code=404, detail=f"Sheet '{sheet_name}' not found")

            # Delete the sheet
            request = {
                'requests': [{
                    'deleteSheet': {
                        'sheetId': sheet_to_delete
                    }
                }]
            }
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body=request
            ).execute()

            return {"status": "success", "message": f"Sheet '{sheet_name}' deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def duplicate_sheet(sheet_id: str, source_name: str, new_name: str):
        """Duplicate a sheet and place it after the source sheet"""
        service = SheetsService._get_service()
        try:
            # Get source sheet info
            spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            source_sheet_id = None
            source_index = 0
            
            for i, sheet in enumerate(spreadsheet['sheets']):
                if sheet['properties']['title'] == source_name:
                    source_sheet_id = sheet['properties']['sheetId']
                    source_index = i
                    break
            
            if source_sheet_id is None:
                raise HTTPException(status_code=404, detail=f"Sheet '{source_name}' not found")

            # Create duplicate request with proper index
            request = {
                'requests': [{
                    'duplicateSheet': {
                        'sourceSheetId': source_sheet_id,
                        'insertSheetIndex': source_index + 1,  # Insert right after source sheet
                        'newSheetName': new_name
                    }
                }]
            }
            
            # Execute the duplicate request
            service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body=request
            ).execute()

            return {"status": "success", "message": f"Sheet '{source_name}' duplicated as '{new_name}'"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def rename_sheet(sheet_id: str, old_name: str, new_name: str):
        """Rename a sheet"""
        service = SheetsService._get_service()
        try:
            # Get all sheets to find the sheet ID
            spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            sheet_to_rename = None
            
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == old_name:
                    sheet_to_rename = sheet['properties']['sheetId']
                    break
            
            if sheet_to_rename is None:
                raise HTTPException(status_code=404, detail=f"Sheet '{old_name}' not found")

            # Create rename request
            request = {
                'requests': [{
                    'updateSheetProperties': {
                        'properties': {
                            'sheetId': sheet_to_rename,
                            'title': new_name
                        },
                        'fields': 'title'
                    }
                }]
            }
            
            # Execute the rename request
            service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body=request
            ).execute()

            return {
                "status": "success", 
                "message": f"Sheet renamed from '{old_name}' to '{new_name}'"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def format_cell(sheet_id: str, cell_range: str, format_data: dict):
        """Update cell formatting"""
        service = SheetsService._get_service()
        try:
            # Convert A1 notation to row/column indices
            col = ord(cell_range[0]) - ord('A')
            row = int(cell_range[1:]) - 1

            # Define color mappings
            color_map = {
                'red': {'red': 0.99, 'green': 0.91, 'blue': 0.91},
                'green': {'red': 0.90, 'green': 0.96, 'blue': 0.92},
                'yellow': {'red': 0.99, 'green': 0.97, 'blue': 0.88},
                'blue': {'red': 0.91, 'green': 0.94, 'blue': 0.99},
                '': {'red': 1, 'green': 1, 'blue': 1}  # white/reset
            }

            request = {
                'requests': [{
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,  # Assumes first sheet
                            'startRowIndex': row,
                            'endRowIndex': row + 1,
                            'startColumnIndex': col,
                            'endColumnIndex': col + 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': color_map[format_data['backgroundColor']]
                            }
                        },
                        'fields': 'userEnteredFormat.backgroundColor'
                    }
                }]
            }

            result = service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body=request
            ).execute()

            return {"status": "success", "result": result}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) 