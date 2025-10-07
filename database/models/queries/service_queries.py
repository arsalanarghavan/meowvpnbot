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
        user_id=user_id, plan_id=plan.id, username_in_panel=panel_username,
        start_date=start_date, expire_date=expire_date
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

def get_user_active_services(db: Session, user_id: int) -> List[Service]:
    """Fetches all non-cancelled services for a specific user."""
    return db.query(Service).filter(Service.user_id == user_id, Service.is_active == True).all()

def get_service_by_id(db: Session, service_id: int) -> Service:
    """Fetches a service by its primary ID."""
    return db.query(Service).filter(Service.id == service_id).first()

def get_expiring_services_with_auto_renew(db: Session) -> List[Service]:
    """Fetches active services with auto-renew enabled that are expiring within the next 24 hours."""
    tomorrow = datetime.utcnow() + timedelta(days=1)
    return db.query(Service).filter(
        Service.is_active == True,
        Service.auto_renew == True,
        Service.expire_date <= tomorrow
    ).all()

def update_service_note(db: Session, service_id: int, new_note: str) -> Service:
    """Updates the note for a specific service."""
    service = get_service_by_id(db, service_id)
    if service:
        service.note = new_note
        db.commit()
        db.refresh(service)
    return service

def renew_service_record(db: Session, service: Service) -> Service:
    """Extends the expiration date of a service based on its plan's duration."""
    now = datetime.utcnow()
    # If the service is already expired, renew from now. Otherwise, add to the expiry date.
    start_date = service.expire_date if service.expire_date > now else now
    duration = service.plan.duration_days
    service.expire_date = start_date + timedelta(days=duration)
    db.commit()
    db.refresh(service)
    return service

def toggle_auto_renew(db: Session, service_id: int) -> Service:
    """Toggles the auto_renew status for a specific service."""
    service = get_service_by_id(db, service_id)
    if service:
        service.auto_renew = not service.auto_renew
        db.commit()
        db.refresh(service)
    return service

def cancel_service_record(db: Session, service_id: int) -> Service:
    """Marks a service as inactive (cancelled)."""
    service = get_service_by_id(db, service_id)
    if service:
        service.is_active = False
        db.commit()
        db.refresh(service)
    return service