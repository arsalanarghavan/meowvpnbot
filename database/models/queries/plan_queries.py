from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.models.plan import Plan, PlanCategory

def get_test_plan(db: Session) -> Plan:
    """Fetches the test plan from the database."""
    return db.query(Plan).filter(Plan.is_test_plan == True).first()

def get_plans_by_category(db: Session, category: PlanCategory) -> List[Plan]:
    """Fetches all plans belonging to a specific category."""
    return db.query(Plan).filter(Plan.category == category, Plan.is_test_plan == False).order_by(Plan.price).all()

def get_plan_by_id(db: Session, plan_id: int) -> Plan:
    """Fetches a single plan by its ID."""
    return db.query(Plan).filter(Plan.id == plan_id).first()

def get_all_plans(db: Session) -> List[Plan]:
    """Fetches all non-test plans from the database."""
    return db.query(Plan).filter(Plan.is_test_plan == False).order_by(Plan.category, Plan.price).all()

def create_plan(db: Session, plan_data: Dict[str, Any]) -> Plan:
    """Creates a new plan in the database."""
    new_plan = Plan(
        name=plan_data['name'],
        category=plan_data['category'],
        duration_days=plan_data['duration'],
        traffic_gb=plan_data['traffic'],
        price=plan_data['price'],
        device_limit=plan_data['device_limit']
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan