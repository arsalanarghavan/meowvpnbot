from sqlalchemy.orm import Session
from database.models.setting import Setting
from typing import Optional
from core.cache import get_cache, set_cache, delete_cache

# Cache TTL for settings (5 minutes)
SETTING_CACHE_TTL = 300

def get_setting(db: Session, key: str, default: Optional[str] = None) -> str:
    """
    Retrieves a setting value from the database.
    Returns the default value if the key is not found.
    Uses caching to reduce database queries.
    """
    # Try cache first
    cache_key = f"setting:{key}"
    cached_value = get_cache(cache_key)
    if cached_value is not None:
        return cached_value
    
    # Query database
    setting = db.query(Setting).filter(Setting.key == key).first()
    value = setting.value if setting and setting.value is not None else default
    
    # Cache the result
    set_cache(cache_key, value, SETTING_CACHE_TTL)
    
    return value

def update_setting(db: Session, key: str, value: str):
    """
    Creates or updates a setting in the database.
    Invalidates cache for this setting.
    """
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.add(setting)
    db.commit()
    
    # Invalidate cache
    cache_key = f"setting:{key}"
    delete_cache(cache_key)