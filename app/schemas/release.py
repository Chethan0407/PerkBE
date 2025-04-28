from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class ReleaseStatus(str, Enum):
    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class KitStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    BLOCKED = "Blocked"

class SubtaskStatus(str, Enum):
    TODO = "To-Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

class SubtaskType(str, Enum):
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    TESTING = "Testing"
    DEPLOYMENT = "Deployment"

class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class DependencyType(str, Enum):
    FINISH_TO_START = "finish_to_start"
    START_TO_START = "start_to_start"
    FINISH_TO_FINISH = "finish_to_finish"
    START_TO_FINISH = "start_to_finish"

class VisualizationSettings(BaseModel):
    show_critical_path: bool = True
    show_resource_load: bool = True
    show_task_dependencies: bool = True
    show_milestones: bool = True
    color_scheme: str = "default"
    custom_colors: Optional[Dict[str, str]] = None
    view_filters: Optional[Dict[str, Any]] = None

# Base schemas
class SubtaskBase(BaseModel):
    title: str
    description: str
    type: SubtaskType
    owner: str
    status: SubtaskStatus = SubtaskStatus.TODO
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None

class KitBase(BaseModel):
    name: str
    description: str
    owner: str
    status: KitStatus = KitStatus.NOT_STARTED
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    labels: Optional[List[str]] = None

class ReleasePlanBase(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    status: ReleaseStatus = ReleaseStatus.DRAFT
    priority: Optional[Priority] = None
    release_owner: str
    created_by: str
    company_id: int

class GanttConfig(BaseModel):
    start_date: datetime
    end_date: datetime
    view_mode: str = "month"  # day, week, month, quarter, year
    show_dependencies: bool = True
    show_milestones: bool = True
    show_progress: bool = True
    custom_colors: Optional[Dict[str, str]] = None

class TimelineConfig(BaseModel):
    view_mode: str = "timeline"  # timeline, calendar, list
    group_by: Optional[str] = None  # status, owner, type
    sort_by: str = "start_date"  # start_date, end_date, priority
    show_completed: bool = True
    show_blocked: bool = True

class MilestoneType(str, Enum):
    RELEASE = "release"
    FEATURE = "feature"
    DEADLINE = "deadline"
    MILESTONE = "milestone"

class ReleasePlanMilestoneBase(BaseModel):
    name: str
    description: Optional[str] = None
    date: datetime
    type: MilestoneType
    color: Optional[str] = None

class ReleasePlanSheetBase(BaseModel):
    name: str
    description: Optional[str] = None
    gantt_config: Optional[GanttConfig] = None
    timeline_config: Optional[TimelineConfig] = None
    visualization_settings: Optional[VisualizationSettings] = None

class ReleasePlanRowBase(BaseModel):
    row_number: int
    data: dict

# Create schemas
class SubtaskCreate(SubtaskBase):
    dependencies: Optional[List[TaskDependencyCreate]] = None
    resource_allocations: Optional[List[ResourceAllocationCreate]] = None

class KitCreate(KitBase):
    subtasks: Optional[List[SubtaskCreate]] = None

class ReleasePlanCreate(ReleasePlanBase):
    kits: Optional[List[KitCreate]] = None

class ReleasePlanSheetCreate(ReleasePlanSheetBase):
    pass

class ReleasePlanRowCreate(ReleasePlanRowBase):
    pass

# Response schemas
class Subtask(SubtaskBase):
    id: UUID
    kit_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    outgoing_dependencies: List[TaskDependency] = []
    incoming_dependencies: List[TaskDependency] = []
    resource_allocations: List[ResourceAllocation] = []

    class Config:
        from_attributes = True

class Kit(KitBase):
    id: UUID
    release_plan_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    subtasks: List[Subtask] = []

    class Config:
        from_attributes = True

class ReleasePlanSheet(ReleasePlanSheetBase):
    id: UUID
    release_plan_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    rows: List[ReleasePlanRow] = []
    milestones: List[ReleasePlanMilestone] = []

    class Config:
        from_attributes = True

class ReleasePlanRow(ReleasePlanRowBase):
    id: int
    sheet_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReleasePlan(ReleasePlanBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    progress_percentage: int = 0
    kits: List[Kit] = []
    sheet: Optional[ReleasePlanSheet] = None

    class Config:
        from_attributes = True

class ReleasePlanMilestoneCreate(ReleasePlanMilestoneBase):
    pass

class ReleasePlanMilestone(ReleasePlanMilestoneBase):
    id: UUID
    sheet_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Update schemas
class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[SubtaskType] = None
    owner: Optional[str] = None
    status: Optional[SubtaskStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None

class KitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[KitStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    labels: Optional[List[str]] = None

class ReleasePlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ReleaseStatus] = None
    priority: Optional[Priority] = None
    release_owner: Optional[str] = None
    progress_percentage: Optional[int] = None

class TaskDependencyBase(BaseModel):
    source_task_id: UUID
    target_task_id: UUID
    dependency_type: DependencyType
    lag_days: int = 0

class TaskDependencyCreate(TaskDependencyBase):
    pass

class TaskDependency(TaskDependencyBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResourceAllocationBase(BaseModel):
    user_id: str
    allocation_percentage: int = Field(..., ge=0, le=100)
    start_date: datetime
    end_date: datetime

class ResourceAllocationCreate(ResourceAllocationBase):
    pass

class ResourceAllocation(ResourceAllocationBase):
    id: UUID
    subtask_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 