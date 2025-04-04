from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ReleasePlan(Base):
    __tablename__ = "release_plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    release_date = Column(DateTime, nullable=False)
    status = Column(String(50))  # Draft, In Review, Approved, Completed
    version = Column(String(50))
    owner_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship("Document", back_populates="release_plan")
    comments = relationship("Comment", back_populates="release_plan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    file_path = Column(String(512))
    release_plan_id = Column(Integer, ForeignKey("release_plans.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    release_plan = relationship("ReleasePlan", back_populates="documents")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    user_id = Column(Integer)
    release_plan_id = Column(Integer, ForeignKey("release_plans.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    release_plan = relationship("ReleasePlan", back_populates="comments") 