from typing import List
from sqlalchemy.orm import Session
from database.models.plan import Plan, PlanCategory

def get_test_plan(db: Session) -> Plan:
    """Fetches the test plan from the database."""
    return db.query(Plan).filter(Plan.is_test_plan == True).first()

def get_plans_by_category(db: Session, category: PlanCategory) -> List[Plan]:
    """Fetches all plans belonging to a specific category."""
    return db.query(Plan).filter(Plan.category == category, Plan.is_test_plan == False).all()

# ---> تابع جدید <---
def get_plan_by_id(db: Session, plan_id: int) -> Plan:
    """Fetches a single plan by its ID."""
    return db.query(Plan).filter(Plan.id == plan_id).first()