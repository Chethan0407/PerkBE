from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.schema import Index
from app.core.database import Base

class Sheet(Base):
    __tablename__ = "sheets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    rows = Column(Integer, default=100)
    columns = Column(Integer, default=26)
    is_template = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cells = relationship("Cell", back_populates="sheet", cascade="all, delete-orphan")

class Cell(Base):
    __tablename__ = "cells"

    id = Column(Integer, primary_key=True, index=True)
    sheet_id = Column(Integer, ForeignKey("sheets.id"))
    row = Column(Integer)
    column = Column(Integer)
    value = Column(String)
    style = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sheet = relationship("Sheet", back_populates="cells")

    __table_args__ = (
        {'sqlite_autoincrement': True},
        Index('ix_cells_sheet_row_column', 'sheet_id', 'row', 'column', unique=True),
    ) 