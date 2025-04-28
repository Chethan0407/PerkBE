from sqlalchemy.orm import Session
from app.models.database import ReleasePlan, Kit, Subtask, ReleasePlanSheet, ReleasePlanRow, ReleasePlanMilestone, TaskDependency, ResourceAllocation
from app.schemas.release import (
    ReleasePlanCreate, ReleasePlanUpdate,
    KitCreate, KitUpdate,
    SubtaskCreate, SubtaskUpdate,
    ReleasePlanSheetCreate, ReleasePlanRowCreate,
    ReleasePlanMilestoneCreate, GanttConfig, TimelineConfig,
    TaskDependencyCreate, ResourceAllocationCreate,
    VisualizationSettings
)
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

# Release Plan operations
def create_release_plan_sheet(db: Session, release_plan_id: str) -> ReleasePlanSheet:
    # Create default Gantt and Timeline configs
    gantt_config = GanttConfig(
        start_date=datetime.now(),
        end_date=datetime.now(),
        view_mode="month"
    )
    
    timeline_config = TimelineConfig(
        view_mode="timeline",
        group_by="status",
        sort_by="start_date"
    )
    
    sheet_data = ReleasePlanSheetCreate(
        name=f"Release Plan Sheet - {release_plan_id}",
        description="Auto-generated sheet for release plan",
        gantt_config=gantt_config,
        timeline_config=timeline_config
    )
    
    db_sheet = ReleasePlanSheet(**sheet_data.dict(), release_plan_id=release_plan_id)
    db.add(db_sheet)
    db.commit()
    db.refresh(db_sheet)
    return db_sheet

def create_release_plan(db: Session, release_plan: ReleasePlanCreate) -> ReleasePlan:
    # Create the release plan
    db_release_plan = ReleasePlan(**release_plan.dict(exclude={"kits"}))
    db.add(db_release_plan)
    db.commit()
    db.refresh(db_release_plan)
    
    # Auto-create the sheet for this release plan
    create_release_plan_sheet(db, db_release_plan.id)
    
    # Create kits if provided
    if release_plan.kits:
        for kit_data in release_plan.kits:
            create_kit(db, kit_data, db_release_plan.id)
    
    return db_release_plan

def get_release_plan(db: Session, release_plan_id: str) -> Optional[ReleasePlan]:
    return db.query(ReleasePlan).filter(ReleasePlan.id == release_plan_id).first()

def get_release_plans(
    db: Session,
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> List[ReleasePlan]:
    query = db.query(ReleasePlan).filter(ReleasePlan.company_id == company_id)
    if status:
        query = query.filter(ReleasePlan.status == status)
    return query.offset(skip).limit(limit).all()

def update_release_plan(
    db: Session,
    release_plan_id: str,
    release_plan: ReleasePlanUpdate
) -> Optional[ReleasePlan]:
    db_release_plan = get_release_plan(db, release_plan_id)
    if db_release_plan:
        update_data = release_plan.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_release_plan, key, value)
        db.commit()
        db.refresh(db_release_plan)
    return db_release_plan

def delete_release_plan(db: Session, release_plan_id: str) -> bool:
    db_release_plan = get_release_plan(db, release_plan_id)
    if db_release_plan:
        db.delete(db_release_plan)
        db.commit()
        return True
    return False

# Kit operations
def create_kit(db: Session, kit: KitCreate, release_plan_id: str) -> Kit:
    db_kit = Kit(**kit.dict(exclude={"subtasks"}), release_plan_id=release_plan_id)
    db.add(db_kit)
    db.commit()
    db.refresh(db_kit)
    
    if kit.subtasks:
        for subtask_data in kit.subtasks:
            create_subtask(db, subtask_data, db_kit.id)
    
    return db_kit

def get_kit(db: Session, kit_id: str) -> Optional[Kit]:
    return db.query(Kit).filter(Kit.id == kit_id).first()

def get_kits(
    db: Session,
    release_plan_id: str,
    status: Optional[str] = None
) -> List[Kit]:
    query = db.query(Kit).filter(Kit.release_plan_id == release_plan_id)
    if status:
        query = query.filter(Kit.status == status)
    return query.all()

def update_kit(
    db: Session,
    kit_id: str,
    kit: KitUpdate
) -> Optional[Kit]:
    db_kit = get_kit(db, kit_id)
    if db_kit:
        update_data = kit.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_kit, key, value)
        db.commit()
        db.refresh(db_kit)
    return db_kit

def delete_kit(db: Session, kit_id: str) -> bool:
    db_kit = get_kit(db, kit_id)
    if db_kit:
        db.delete(db_kit)
        db.commit()
        return True
    return False

# Subtask operations
def create_subtask(db: Session, subtask: SubtaskCreate, kit_id: str) -> Subtask:
    # Create the subtask
    db_subtask = Subtask(**subtask.dict(exclude={"dependencies", "resource_allocations"}), kit_id=kit_id)
    db.add(db_subtask)
    db.commit()
    db.refresh(db_subtask)
    
    # Create dependencies if provided
    if subtask.dependencies:
        for dependency in subtask.dependencies:
            create_task_dependency(db, dependency, db_subtask.id)
    
    # Create resource allocations if provided
    if subtask.resource_allocations:
        for allocation in subtask.resource_allocations:
            create_resource_allocation(db, allocation, db_subtask.id)
    
    return db_subtask

def get_subtask(db: Session, subtask_id: str) -> Optional[Subtask]:
    return db.query(Subtask).filter(Subtask.id == subtask_id).first()

def get_subtasks(
    db: Session,
    kit_id: str,
    status: Optional[str] = None
) -> List[Subtask]:
    query = db.query(Subtask).filter(Subtask.kit_id == kit_id)
    if status:
        query = query.filter(Subtask.status == status)
    return query.all()

def update_subtask(
    db: Session,
    subtask_id: str,
    subtask: SubtaskUpdate
) -> Optional[Subtask]:
    db_subtask = get_subtask(db, subtask_id)
    if db_subtask:
        update_data = subtask.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_subtask, key, value)
        db.commit()
        db.refresh(db_subtask)
    return db_subtask

def delete_subtask(db: Session, subtask_id: str) -> bool:
    db_subtask = get_subtask(db, subtask_id)
    if db_subtask:
        db.delete(db_subtask)
        db.commit()
        return True
    return False

# Progress calculation
def calculate_release_progress(db: Session, release_plan_id: str) -> Dict[str, Any]:
    release_plan = get_release_plan(db, release_plan_id)
    if not release_plan:
        return {"progress_percentage": 0, "details": {}}
    
    kits = get_kits(db, release_plan_id)
    if not kits:
        return {"progress_percentage": 0, "details": {}}
    
    total_kits = len(kits)
    completed_kits = sum(1 for kit in kits if kit.status == "Done")
    progress_percentage = int((completed_kits / total_kits) * 100) if total_kits > 0 else 0
    
    # Calculate progress by status
    status_counts = {}
    for kit in kits:
        status_counts[kit.status] = status_counts.get(kit.status, 0) + 1
    
    # Calculate progress by owner
    owner_progress = {}
    for kit in kits:
        if kit.owner not in owner_progress:
            owner_progress[kit.owner] = {"total": 0, "completed": 0}
        owner_progress[kit.owner]["total"] += 1
        if kit.status == "Done":
            owner_progress[kit.owner]["completed"] += 1
    
    return {
        "progress_percentage": progress_percentage,
        "details": {
            "total_kits": total_kits,
            "completed_kits": completed_kits,
            "status_counts": status_counts,
            "owner_progress": owner_progress
        }
    }

def update_sheet_config(
    db: Session,
    sheet_id: str,
    gantt_config: Optional[GanttConfig] = None,
    timeline_config: Optional[TimelineConfig] = None
) -> Optional[ReleasePlanSheet]:
    db_sheet = db.query(ReleasePlanSheet).filter(ReleasePlanSheet.id == sheet_id).first()
    if db_sheet:
        if gantt_config:
            db_sheet.gantt_config = gantt_config.dict()
        if timeline_config:
            db_sheet.timeline_config = timeline_config.dict()
        db.commit()
        db.refresh(db_sheet)
    return db_sheet

def create_milestone(
    db: Session,
    sheet_id: str,
    milestone: ReleasePlanMilestoneCreate
) -> ReleasePlanMilestone:
    db_milestone = ReleasePlanMilestone(**milestone.dict(), sheet_id=sheet_id)
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone

def get_milestones(
    db: Session,
    sheet_id: str,
    type: Optional[str] = None
) -> List[ReleasePlanMilestone]:
    query = db.query(ReleasePlanMilestone).filter(ReleasePlanMilestone.sheet_id == sheet_id)
    if type:
        query = query.filter(ReleasePlanMilestone.type == type)
    return query.all()

def update_milestone(
    db: Session,
    milestone_id: str,
    milestone: ReleasePlanMilestoneCreate
) -> Optional[ReleasePlanMilestone]:
    db_milestone = db.query(ReleasePlanMilestone).filter(ReleasePlanMilestone.id == milestone_id).first()
    if db_milestone:
        update_data = milestone.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_milestone, key, value)
        db.commit()
        db.refresh(db_milestone)
    return db_milestone

def delete_milestone(db: Session, milestone_id: str) -> bool:
    db_milestone = db.query(ReleasePlanMilestone).filter(ReleasePlanMilestone.id == milestone_id).first()
    if db_milestone:
        db.delete(db_milestone)
        db.commit()
        return True
    return False

def create_task_dependency(
    db: Session,
    dependency: TaskDependencyCreate,
    source_task_id: str
) -> TaskDependency:
    db_dependency = TaskDependency(**dependency.dict(), source_task_id=source_task_id)
    db.add(db_dependency)
    db.commit()
    db.refresh(db_dependency)
    return db_dependency

def create_resource_allocation(
    db: Session,
    allocation: ResourceAllocationCreate,
    subtask_id: str
) -> ResourceAllocation:
    db_allocation = ResourceAllocation(**allocation.dict(), subtask_id=subtask_id)
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    return db_allocation

def get_task_dependencies(
    db: Session,
    task_id: str,
    direction: str = "all"  # "incoming", "outgoing", or "all"
) -> List[TaskDependency]:
    query = db.query(TaskDependency)
    if direction == "incoming":
        query = query.filter(TaskDependency.target_task_id == task_id)
    elif direction == "outgoing":
        query = query.filter(TaskDependency.source_task_id == task_id)
    else:
        query = query.filter(
            (TaskDependency.source_task_id == task_id) |
            (TaskDependency.target_task_id == task_id)
        )
    return query.all()

def get_resource_allocations(
    db: Session,
    subtask_id: Optional[str] = None,
    user_id: Optional[str] = None,
    date_range: Optional[Dict[str, datetime]] = None
) -> List[ResourceAllocation]:
    query = db.query(ResourceAllocation)
    
    if subtask_id:
        query = query.filter(ResourceAllocation.subtask_id == subtask_id)
    if user_id:
        query = query.filter(ResourceAllocation.user_id == user_id)
    if date_range:
        if "start" in date_range:
            query = query.filter(ResourceAllocation.start_date >= date_range["start"])
        if "end" in date_range:
            query = query.filter(ResourceAllocation.end_date <= date_range["end"])
    
    return query.all()

def calculate_critical_path(db: Session, release_plan_id: str) -> Dict[str, Any]:
    # Get all subtasks in the release plan
    subtasks = []
    for kit in get_kits(db, release_plan_id):
        subtasks.extend(get_subtasks(db, kit.id))
    
    if not subtasks:
        return {"critical_path": [], "total_duration": 0}
    
    # Calculate earliest start and finish times
    for subtask in subtasks:
        incoming_deps = get_task_dependencies(db, str(subtask.id), "incoming")
        if not incoming_deps:
            subtask.earliest_start = subtask.start_date
        else:
            latest_finish = max(
                dep.source_task.earliest_finish + timedelta(days=dep.lag_days)
                for dep in incoming_deps
            )
            subtask.earliest_start = latest_finish
        
        subtask.earliest_finish = subtask.earliest_start + timedelta(hours=subtask.estimated_hours or 0)
    
    # Calculate latest start and finish times
    for subtask in reversed(subtasks):
        outgoing_deps = get_task_dependencies(db, str(subtask.id), "outgoing")
        if not outgoing_deps:
            subtask.latest_finish = subtask.end_date or subtask.earliest_finish
        else:
            earliest_start = min(
                dep.target_task.latest_start - timedelta(days=dep.lag_days)
                for dep in outgoing_deps
            )
            subtask.latest_finish = earliest_start
        
        subtask.latest_start = subtask.latest_finish - timedelta(hours=subtask.estimated_hours or 0)
    
    # Identify critical path
    critical_path = []
    for subtask in subtasks:
        if subtask.earliest_start == subtask.latest_start and subtask.earliest_finish == subtask.latest_finish:
            critical_path.append({
                "subtask_id": str(subtask.id),
                "title": subtask.title,
                "start_date": subtask.earliest_start,
                "end_date": subtask.earliest_finish,
                "duration_hours": subtask.estimated_hours
            })
    
    total_duration = sum(task["duration_hours"] for task in critical_path) if critical_path else 0
    
    return {
        "critical_path": critical_path,
        "total_duration": total_duration
    }

def calculate_resource_load(
    db: Session,
    user_id: str,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    allocations = get_resource_allocations(
        db,
        user_id=user_id,
        date_range={"start": start_date, "end": end_date}
    )
    
    daily_load = {}
    for allocation in allocations:
        current_date = allocation.start_date
        while current_date <= allocation.end_date:
            if current_date not in daily_load:
                daily_load[current_date] = 0
            daily_load[current_date] += allocation.allocation_percentage
            current_date += timedelta(days=1)
    
    return {
        "user_id": user_id,
        "period": {
            "start": start_date,
            "end": end_date
        },
        "daily_load": daily_load,
        "average_load": sum(daily_load.values()) / len(daily_load) if daily_load else 0,
        "max_load": max(daily_load.values()) if daily_load else 0
    } 