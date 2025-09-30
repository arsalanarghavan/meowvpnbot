from typing import List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models.service import Service
from database.models.plan import Plan

def create_service_record(db: Session, user_id: int, plan: Plan, panel_username: str) -> Service:
    """Creates a new service record for a user after a successful purchase."""
    
    start_date = datetime.utcnow()
    expire_date = start_date + timedelta(days=plan.duration_days)
    
    new_service = Service(
        user_id=user_id,
        plan_id=plan.id,
        username_in_panel=panel_username,
        start_date=start_date,
        expire_date=expire_date
    )
    
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

def get_user_active_services(db: Session, user_id: int) -> List[Service]:
    """Fetches all active services for a specific user."""
    return db.query(Service).filter(
        Service.user_id == user_id,
        Service.is_active == True,
        Service.expire_date > datetime.utcnow()
    ).all()

def get_service_by_id(db: Session, service_id: int) -> Service:
    """Fetches a service by its primary ID."""
    return db.query(Service).filter(Service.id == service_id).first()

def update_service_note(db: Session, service_id: int, new_note: str) -> Service:
    """Updates the note for a specific service."""
    service = get_service_by_id(db, service_id)
    if service:
        service.note = new_note
        db.commit()
        db.refresh(service)
    return service