from sqlalchemy.orm import Session
from app.models.database import ReleasePlan
from app.db.database import get_db
from fastapi import Depends
from datetime import datetime

class ReleasePlanService:
    @staticmethod
    async def get_all(db: Session = Depends(get_db)):
        return db.query(ReleasePlan).all()

    @staticmethod
    async def get_by_id(plan_id: int, db: Session = Depends(get_db)):
        return db.query(ReleasePlan).filter(ReleasePlan.id == plan_id).first()

    @staticmethod
    async def create(plan_data, db: Session = Depends(get_db)):
        db_plan = ReleasePlan(**plan_data.dict())
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan

    @staticmethod
    async def update(plan_id: int, plan_data, db: Session = Depends(get_db)):
        db_plan = db.query(ReleasePlan).filter(ReleasePlan.id == plan_id).first()
        if db_plan:
            for key, value in plan_data.dict(exclude_unset=True).items():
                setattr(db_plan, key, value)
            db_plan.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_plan)
        return db_plan

    @staticmethod
    async def delete(plan_id: int, db: Session = Depends(get_db)):
        db_plan = db.query(ReleasePlan).filter(ReleasePlan.id == plan_id).first()
        if db_plan:
            db.delete(db_plan)
            db.commit()
        return {"status": "success"} 