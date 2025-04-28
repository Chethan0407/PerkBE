from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.release import (
    ReleasePlan, ReleasePlanCreate, ReleasePlanUpdate,
    Kit, KitCreate, KitUpdate,
    Subtask, SubtaskCreate, SubtaskUpdate,
    ReleasePlanSheet, ReleasePlanMilestone, ReleasePlanMilestoneCreate,
    GanttConfig, TimelineConfig, VisualizationSettings,
    TaskDependency, TaskDependencyCreate,
    ResourceAllocation, ResourceAllocationCreate
)
from app.services.release_service import (
    create_release_plan, get_release_plan, get_release_plans,
    update_release_plan, delete_release_plan,
    create_kit, get_kit, get_kits,
    update_kit, delete_kit,
    create_subtask, get_subtask, get_subtasks,
    update_subtask, delete_subtask,
    calculate_release_progress,
    update_sheet_config, create_milestone, get_milestones,
    update_milestone, delete_milestone,
    create_task_dependency, get_task_dependencies,
    create_resource_allocation, get_resource_allocations,
    calculate_critical_path, calculate_resource_load
)

router = APIRouter()

# Release Plan endpoints
@router.post("/release-plans", response_model=ReleasePlan)
def create_release_plan_endpoint(
    release_plan: ReleasePlanCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new release plan
    """
    return create_release_plan(db=db, release_plan=release_plan)

@router.get("/release-plans", response_model=List[ReleasePlan])
def get_all_release_plans(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all release plans with optional filtering
    """
    return get_release_plans(db, skip=skip, limit=limit, status=status)

@router.get("/release-plans/{release_plan_id}", response_model=ReleasePlan)
def get_release_plan_endpoint(
    release_plan_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific release plan by ID
    """
    db_release_plan = get_release_plan(db, release_plan_id=release_plan_id)
    if db_release_plan is None:
        raise HTTPException(status_code=404, detail="Release plan not found")
    return db_release_plan

@router.put("/release-plans/{release_plan_id}", response_model=ReleasePlan)
def update_release_plan_endpoint(
    release_plan_id: str,
    release_plan: ReleasePlanUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a release plan
    """
    db_release_plan = update_release_plan(db, release_plan_id=release_plan_id, release_plan=release_plan)
    if db_release_plan is None:
        raise HTTPException(status_code=404, detail="Release plan not found")
    return db_release_plan

@router.delete("/release-plans/{release_plan_id}")
def delete_release_plan_endpoint(
    release_plan_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a release plan
    """
    if not delete_release_plan(db, release_plan_id=release_plan_id):
        raise HTTPException(status_code=404, detail="Release plan not found")
    return {"message": "Release plan deleted successfully"}

# Kit endpoints
@router.post("/release-plans/{release_plan_id}/kits", response_model=Kit)
def create_new_kit(
    release_plan_id: str,
    kit: KitCreate,
    db: Session = Depends(get_db)
):
    return create_kit(db=db, kit=kit, release_plan_id=release_plan_id)

@router.get("/release-plans/{release_plan_id}/kits", response_model=List[Kit])
def read_kits(
    release_plan_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_kits(db, release_plan_id=release_plan_id, status=status)

@router.get("/kits/{kit_id}", response_model=Kit)
def read_kit(kit_id: str, db: Session = Depends(get_db)):
    db_kit = get_kit(db, kit_id=kit_id)
    if db_kit is None:
        raise HTTPException(status_code=404, detail="Kit not found")
    return db_kit

@router.put("/kits/{kit_id}", response_model=Kit)
def update_kit_endpoint(
    kit_id: str,
    kit: KitUpdate,
    db: Session = Depends(get_db)
):
    db_kit = update_kit(db, kit_id=kit_id, kit=kit)
    if db_kit is None:
        raise HTTPException(status_code=404, detail="Kit not found")
    return db_kit

@router.delete("/kits/{kit_id}")
def delete_kit_endpoint(kit_id: str, db: Session = Depends(get_db)):
    if not delete_kit(db, kit_id=kit_id):
        raise HTTPException(status_code=404, detail="Kit not found")
    return {"message": "Kit deleted successfully"}

# Subtask endpoints
@router.post("/kits/{kit_id}/subtasks", response_model=Subtask)
def create_new_subtask(
    kit_id: str,
    subtask: SubtaskCreate,
    db: Session = Depends(get_db)
):
    return create_subtask(db=db, subtask=subtask, kit_id=kit_id)

@router.get("/kits/{kit_id}/subtasks", response_model=List[Subtask])
def read_subtasks(
    kit_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_subtasks(db, kit_id=kit_id, status=status)

@router.get("/subtasks/{subtask_id}", response_model=Subtask)
def read_subtask(subtask_id: str, db: Session = Depends(get_db)):
    db_subtask = get_subtask(db, subtask_id=subtask_id)
    if db_subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return db_subtask

@router.put("/subtasks/{subtask_id}", response_model=Subtask)
def update_subtask_endpoint(
    subtask_id: str,
    subtask: SubtaskUpdate,
    db: Session = Depends(get_db)
):
    db_subtask = update_subtask(db, subtask_id=subtask_id, subtask=subtask)
    if db_subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return db_subtask

@router.delete("/subtasks/{subtask_id}")
def delete_subtask_endpoint(subtask_id: str, db: Session = Depends(get_db)):
    if not delete_subtask(db, subtask_id=subtask_id):
        raise HTTPException(status_code=404, detail="Subtask not found")
    return {"message": "Subtask deleted successfully"}

# Sheet configuration endpoints
@router.put("/sheets/{sheet_id}/config", response_model=ReleasePlanSheet)
def update_sheet_config_endpoint(
    sheet_id: str,
    gantt_config: Optional[GanttConfig] = None,
    timeline_config: Optional[TimelineConfig] = None,
    db: Session = Depends(get_db)
):
    db_sheet = update_sheet_config(db, sheet_id, gantt_config, timeline_config)
    if db_sheet is None:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return db_sheet

# Milestone endpoints
@router.post("/sheets/{sheet_id}/milestones", response_model=ReleasePlanMilestone)
def create_new_milestone(
    sheet_id: str,
    milestone: ReleasePlanMilestoneCreate,
    db: Session = Depends(get_db)
):
    return create_milestone(db, sheet_id, milestone)

@router.get("/sheets/{sheet_id}/milestones", response_model=List[ReleasePlanMilestone])
def read_milestones(
    sheet_id: str,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_milestones(db, sheet_id, type)

@router.put("/milestones/{milestone_id}", response_model=ReleasePlanMilestone)
def update_milestone_endpoint(
    milestone_id: str,
    milestone: ReleasePlanMilestoneCreate,
    db: Session = Depends(get_db)
):
    db_milestone = update_milestone(db, milestone_id, milestone)
    if db_milestone is None:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return db_milestone

@router.delete("/milestones/{milestone_id}")
def delete_milestone_endpoint(milestone_id: str, db: Session = Depends(get_db)):
    if not delete_milestone(db, milestone_id):
        raise HTTPException(status_code=404, detail="Milestone not found")
    return {"message": "Milestone deleted successfully"}

# Enhanced progress endpoint
@router.get("/release-plans/{release_plan_id}/progress")
def get_release_progress(release_plan_id: str, db: Session = Depends(get_db)):
    return calculate_release_progress(db, release_plan_id)

# Dependency endpoints
@router.post("/subtasks/{subtask_id}/dependencies", response_model=TaskDependency)
def create_new_dependency(
    subtask_id: str,
    dependency: TaskDependencyCreate,
    db: Session = Depends(get_db)
):
    return create_task_dependency(db, dependency, subtask_id)

@router.get("/subtasks/{subtask_id}/dependencies", response_model=List[TaskDependency])
def read_dependencies(
    subtask_id: str,
    direction: str = "all",
    db: Session = Depends(get_db)
):
    return get_task_dependencies(db, subtask_id, direction)

# Resource allocation endpoints
@router.post("/subtasks/{subtask_id}/allocations", response_model=ResourceAllocation)
def create_new_allocation(
    subtask_id: str,
    allocation: ResourceAllocationCreate,
    db: Session = Depends(get_db)
):
    return create_resource_allocation(db, allocation, subtask_id)

@router.get("/subtasks/{subtask_id}/allocations", response_model=List[ResourceAllocation])
def read_allocations(
    subtask_id: str,
    db: Session = Depends(get_db)
):
    return get_resource_allocations(db, subtask_id=subtask_id)

@router.get("/users/{user_id}/allocations", response_model=List[ResourceAllocation])
def read_user_allocations(
    user_id: str,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    return get_resource_allocations(
        db,
        user_id=user_id,
        date_range={"start": start_date, "end": end_date}
    )

# Analysis endpoints
@router.get("/release-plans/{release_plan_id}/critical-path")
def get_critical_path(release_plan_id: str, db: Session = Depends(get_db)):
    return calculate_critical_path(db, release_plan_id)

@router.get("/users/{user_id}/resource-load")
def get_resource_load(
    user_id: str,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    return calculate_resource_load(db, user_id, start_date, end_date)

# Visualization settings endpoint
@router.put("/sheets/{sheet_id}/visualization", response_model=ReleasePlanSheet)
def update_visualization_settings(
    sheet_id: str,
    settings: VisualizationSettings,
    db: Session = Depends(get_db)
):
    db_sheet = update_sheet_config(db, sheet_id, visualization_settings=settings)
    if db_sheet is None:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return db_sheet 