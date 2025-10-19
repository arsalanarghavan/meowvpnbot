from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.models.panel import Panel

def get_all_panels(db: Session) -> List[Panel]:
    """Fetches all panels from the database."""
    return db.query(Panel).all()

def get_panel_by_id(db: Session, panel_id: int) -> Panel:
    """Fetches a single panel by its ID."""
    return db.query(Panel).filter(Panel.id == panel_id).first()

def create_panel(db: Session, panel_data: Dict[str, Any]) -> Panel:
    """Creates a new panel in the database."""
    new_panel = Panel(
        name=panel_data['name'],
        panel_type=panel_data['type'],
        api_base_url=panel_data['url'],
        username=panel_data['username'],
        password=panel_data['password']
    )
    db.add(new_panel)
    db.commit()
    db.refresh(new_panel)
    return new_panel

def update_panel(db: Session, panel_id: int, update_data: Dict[str, Any]) -> Panel:
    """Updates a panel's details."""
    panel = db.query(Panel).filter(Panel.id == panel_id).first()
    if panel:
        for key, value in update_data.items():
            setattr(panel, key, value)
        db.commit()
        db.refresh(panel)
    return panel

def delete_panel_by_id(db: Session, panel_id: int) -> bool:
    """Deletes a panel by its ID."""
    panel = db.query(Panel).filter(Panel.id == panel_id).first()
    if panel:
        db.delete(panel)
        db.commit()
        return True
    return False