from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean, Index, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from app.db.base_class import Base
from passlib.context import CryptContext
import enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base = declarative_base()

class ReleaseStatus(enum.Enum):
    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class KitStatus(enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    BLOCKED = "Blocked"

class SubtaskStatus(enum.Enum):
    TODO = "To-Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

class SubtaskType(enum.Enum):
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    TESTING = "Testing"
    DEPLOYMENT = "Deployment"

class Priority(enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("Company", back_populates="users")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sheets = relationship("Sheet", back_populates="company")
    users = relationship("User", back_populates="company")
    release_plans = relationship("ReleasePlan", back_populates="company", cascade="all, delete-orphan")

class Platform(Base):
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sheets = relationship("Sheet", back_populates="platform")

class Sheet(Base):
    __tablename__ = "sheets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    platform_id = Column(Integer, ForeignKey("platforms.id"))
    sheet_type = Column(String)
    description = Column(Text, nullable=True)
    is_template = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("Company", back_populates="sheets")
    platform = relationship("Platform", back_populates="sheets")
    rows = relationship("Row", back_populates="sheet", cascade="all, delete-orphan")

class Row(Base):
    __tablename__ = "rows"

    id = Column(Integer, primary_key=True, index=True)
    sheet_id = Column(UUID(as_uuid=True), ForeignKey("sheets.id"))
    row_number = Column(Integer)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sheet = relationship("Sheet", back_populates="rows")

    __table_args__ = (
        # Ensure each row number is unique within a sheet
        Index('ix_rows_sheet_row_number', 'sheet_id', 'row_number', unique=True),
    )

class ReleasePlan(Base):
    __tablename__ = "release_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(Enum(ReleaseStatus))
    priority = Column(Enum(Priority), nullable=True)
    release_owner = Column(String)
    created_by = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    progress_percentage = Column(Integer, default=0)
    
    company = relationship("Company", back_populates="release_plans")
    kits = relationship("Kit", back_populates="release_plan", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="release_plan", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="release_plan", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="release_plan", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="release_plan", cascade="all, delete-orphan")
    sheet = relationship("ReleasePlanSheet", back_populates="release_plan", uselist=False, cascade="all, delete-orphan")

class ReleasePlanSheet(Base):
    __tablename__ = "release_plan_sheets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    release_plan_id = Column(UUID(as_uuid=True), ForeignKey("release_plans.id"), unique=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    gantt_config = Column(JSON, nullable=True)
    timeline_config = Column(JSON, nullable=True)
    visualization_settings = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    release_plan = relationship("ReleasePlan", back_populates="sheet")
    rows = relationship("ReleasePlanRow", back_populates="sheet", cascade="all, delete-orphan")
    milestones = relationship("ReleasePlanMilestone", back_populates="sheet", cascade="all, delete-orphan")

class ReleasePlanRow(Base):
    __tablename__ = "release_plan_rows"

    id = Column(Integer, primary_key=True, index=True)
    sheet_id = Column(UUID(as_uuid=True), ForeignKey("release_plan_sheets.id"))
    row_number = Column(Integer)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sheet = relationship("ReleasePlanSheet", back_populates="rows")

    __table_args__ = (
        Index('ix_release_plan_rows_sheet_row_number', 'sheet_id', 'row_number', unique=True),
    )

class ReleasePlanMilestone(Base):
    __tablename__ = "release_plan_milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sheet_id = Column(UUID(as_uuid=True), ForeignKey("release_plan_sheets.id"))
    name = Column(String)
    description = Column(Text, nullable=True)
    date = Column(DateTime(timezone=True))
    type = Column(String)  # e.g., "release", "feature", "deadline"
    color = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sheet = relationship("ReleasePlanSheet", back_populates="milestones")

class Kit(Base):
    __tablename__ = "kits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    release_plan_id = Column(UUID(as_uuid=True), ForeignKey("release_plans.id"))
    name = Column(String, index=True)
    description = Column(Text)
    owner = Column(String)
    status = Column(Enum(KitStatus))
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    labels = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    release_plan = relationship("ReleasePlan", back_populates="kits")
    subtasks = relationship("Subtask", back_populates="kit", cascade="all, delete-orphan")

class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id = Column(Integer, primary_key=True, index=True)
    source_task_id = Column(Integer, ForeignKey("subtasks.id"))
    target_task_id = Column(Integer, ForeignKey("subtasks.id"))
    dependency_type = Column(String(50))  # FS, SS, FF, SF
    lag_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    source_task = relationship("Subtask", foreign_keys=[source_task_id], back_populates="outgoing_dependencies")
    target_task = relationship("Subtask", foreign_keys=[target_task_id], back_populates="incoming_dependencies")

class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    kit_id = Column(Integer, ForeignKey("kits.id"))
    title = Column(String(255))
    description = Column(Text)
    type = Column(String(50))  # Development, Testing, Documentation, etc.
    status = Column(String(50), default="not_started")
    priority = Column(String(50), default="medium")
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    kit = relationship("Kit", back_populates="subtasks")
    resource_allocations = relationship("ResourceAllocation", back_populates="subtask")
    outgoing_dependencies = relationship("TaskDependency", foreign_keys=[TaskDependency.source_task_id], back_populates="source_task")
    incoming_dependencies = relationship("TaskDependency", foreign_keys=[TaskDependency.target_task_id], back_populates="target_task")

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    release_plan_id = Column(UUID(as_uuid=True), ForeignKey("release_plans.id"))
    name = Column(String)
    description = Column(Text)
    due_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    release_plan = relationship("ReleasePlan", back_populates="milestones")

class Risk(Base):
    __tablename__ = "risks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    release_plan_id = Column(UUID(as_uuid=True), ForeignKey("release_plans.id"))
    description = Column(Text)
    impact = Column(String)
    probability = Column(String)
    mitigation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    release_plan = relationship("ReleasePlan", back_populates="risks")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    release_plan_id = Column(UUID(as_uuid=True), ForeignKey("release_plans.id"))
    user_id = Column(String)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    release_plan = relationship("ReleasePlan", back_populates="comments")

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    release_plan_id = Column(UUID(as_uuid=True), ForeignKey("release_plans.id"))
    file_name = Column(String)
    file_path = Column(String)
    file_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    release_plan = relationship("ReleasePlan", back_populates="attachments")

class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subtask_id = Column(UUID(as_uuid=True), ForeignKey("subtasks.id"))
    user_id = Column(String)
    allocation_percentage = Column(Integer)  # 0-100
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    subtask = relationship("Subtask", back_populates="resource_allocations") 