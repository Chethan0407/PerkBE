from fastapi import APIRouter, Depends, HTTPException, UploadFile
from typing import List
from app.models.schemas import ReleasePlan, ReleasePlanCreate, ReleasePlanUpdate, CommentCreate
from app.core.auth import get_current_user
from app.services.release_plan_service import ReleasePlanService
from app.services.document_service import DocumentService
from app.services.comment_service import CommentService

router = APIRouter()

# Release Plan Endpoints
@router.get("/release-plans", response_model=List[ReleasePlan])
async def get_all_release_plans(current_user = Depends(get_current_user)):
    """Get all release plans"""
    return await ReleasePlanService.get_all()

@router.get("/release-plans/{plan_id}", response_model=ReleasePlan)
async def get_release_plan(plan_id: int, current_user = Depends(get_current_user)):
    """Get specific release plan"""
    return await ReleasePlanService.get_by_id(plan_id)

@router.post("/release-plans", response_model=ReleasePlan)
async def create_release_plan(plan: ReleasePlanCreate, current_user = Depends(get_current_user)):
    """Create new release plan"""
    return await ReleasePlanService.create(plan)

@router.put("/release-plans/{plan_id}", response_model=ReleasePlan)
async def update_release_plan(
    plan_id: int, 
    plan: ReleasePlanUpdate, 
    current_user = Depends(get_current_user)
):
    """Update existing release plan"""
    return await ReleasePlanService.update(plan_id, plan)

@router.delete("/release-plans/{plan_id}")
async def delete_release_plan(plan_id: int, current_user = Depends(get_current_user)):
    """Delete a release plan"""
    return await ReleasePlanService.delete(plan_id)

# Document Management
@router.post("/release-plans/{plan_id}/documents")
async def upload_document(
    plan_id: int,
    file: UploadFile,
    current_user = Depends(get_current_user)
):
    """Upload document to release plan"""
    return await DocumentService.upload(plan_id, file)

@router.get("/release-plans/{plan_id}/documents")
async def get_documents(plan_id: int, current_user = Depends(get_current_user)):
    """Get all documents for a release plan"""
    return await DocumentService.get_all(plan_id)

# Comments
@router.post("/release-plans/{plan_id}/comments")
async def add_comment(
    plan_id: int,
    comment: CommentCreate,
    current_user = Depends(get_current_user)
):
    """Add comment to release plan"""
    return await CommentService.create(plan_id, comment)

@router.get("/release-plans/{plan_id}/comments")
async def get_comments(plan_id: int, current_user = Depends(get_current_user)):
    """Get all comments for a release plan"""
    return await CommentService.get_all(plan_id) 