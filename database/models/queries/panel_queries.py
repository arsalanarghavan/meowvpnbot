from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.models.panel import Panel

def get_all_panels(db: Session) -> List[Panel]:
    """Fetches all panels from the database."""
    return db.query(Panel).all()

def create_panel(db: Session, panel_data: Dict[str, Any]) -> Panel:
    """Creates a new panel in the database."""
    new_panel = Panel(
        name=panel_data['name'],
        api_base_url=panel_data['url'],
        username=panel_data['username'],
        password=panel_data['password']
    )
    db.add(new_panel)
    db.commit()
    db.refresh(new_panel)
    return new_panel