from sqlalchemy.orm import Session
from database.models.setting import Setting
from typing import Optional

def get_setting(db: Session, key: str, default: Optional[str] = None) -> str:
    """
    Retrieves a setting value from the database.
    Returns the default value if the key is not found.
    """
    setting = db.query(Setting).filter(Setting.key == key).first()
    return setting.value if setting and setting.value is not None else default

def update_setting(db: Session, key: str, value: str):
    """
    Creates or updates a setting in the database.
    """
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.add(setting)
    db.commit()