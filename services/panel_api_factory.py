"""
Factory pattern for creating appropriate Panel API instances based on panel type.
"""

from database.models.panel import Panel, PanelType
from services.marzban_api import MarzbanAPI
from services.hiddify_api import HiddifyAPI
from typing import Union

def get_panel_api(panel: Panel) -> Union[MarzbanAPI, HiddifyAPI]:
    """
    Returns the appropriate API instance based on the panel type.
    
    Args:
        panel: Panel object from database
        
    Returns:
        MarzbanAPI or HiddifyAPI instance
        
    Raises:
        ValueError: If panel type is not recognized
    """
    if panel.panel_type == PanelType.MARZBAN:
        return MarzbanAPI(panel)
    elif panel.panel_type == PanelType.HIDDIFY:
        return HiddifyAPI(panel)
    else:
        raise ValueError(f"Unknown panel type: {panel.panel_type}")

