"""
Input validation utilities for bot handlers.
"""
from typing import Optional, Union
import re
from core.logger import get_logger

logger = get_logger(__name__)


def validate_user_id(user_id: Union[str, int]) -> Optional[int]:
    """
    Validates and converts a user ID to integer.
    
    Args:
        user_id: User ID as string or integer
        
    Returns:
        Validated user ID as integer, or None if invalid
    """
    try:
        user_id_int = int(user_id)
        # Telegram user IDs are positive integers
        if user_id_int > 0:
            return user_id_int
        return None
    except (ValueError, TypeError):
        return None


def validate_amount(amount: Union[str, int, float], min_amount: int = 0, max_amount: Optional[int] = None) -> Optional[int]:
    """
    Validates and converts an amount to integer.
    
    Args:
        amount: Amount as string, integer, or float
        min_amount: Minimum allowed amount
        max_amount: Maximum allowed amount (None for no limit)
        
    Returns:
        Validated amount as integer, or None if invalid
    """
    try:
        amount_int = int(float(amount))
        if amount_int < min_amount:
            return None
        if max_amount is not None and amount_int > max_amount:
            return None
        return amount_int
    except (ValueError, TypeError):
        return None


def validate_positive_integer(value: Union[str, int], min_value: int = 1, max_value: Optional[int] = None) -> Optional[int]:
    """
    Validates a positive integer value.
    
    Args:
        value: Value as string or integer
        min_value: Minimum allowed value
        max_value: Maximum allowed value (None for no limit)
        
    Returns:
        Validated integer, or None if invalid
    """
    try:
        value_int = int(value)
        if value_int < min_value:
            return None
        if max_value is not None and value_int > max_value:
            return None
        return value_int
    except (ValueError, TypeError):
        return None


def validate_text_length(text: str, min_length: int = 0, max_length: int = 1000) -> Optional[str]:
    """
    Validates text length.
    
    Args:
        text: Text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Validated text, or None if invalid
    """
    if not isinstance(text, str):
        return None
    text = text.strip()
    if len(text) < min_length or len(text) > max_length:
        return None
    return text


def validate_url(url: str) -> Optional[str]:
    """
    Validates a URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        Validated URL, or None if invalid
    """
    if not isinstance(url, str):
        return None
    url = url.strip()
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if url_pattern.match(url):
        return url.rstrip('/')
    return None


def validate_card_number(card_number: str) -> Optional[str]:
    """
    Validates a card number (16 digits).
    
    Args:
        card_number: Card number string
        
    Returns:
        Validated card number (digits only), or None if invalid
    """
    if not isinstance(card_number, str):
        return None
    # Remove spaces and dashes
    card_number = re.sub(r'[\s-]', '', card_number)
    # Check if it's 16 digits
    if re.match(r'^\d{16}$', card_number):
        return card_number
    return None


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitizes text input by removing dangerous characters and limiting length.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    # Remove null bytes and control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    return text.strip()


def validate_callback_data(callback_data: str, expected_prefix: str) -> Optional[dict]:
    """
    Validates callback query data format.
    
    Args:
        callback_data: Callback data string
        expected_prefix: Expected prefix (e.g., 'action_')
        
    Returns:
        Dictionary with parsed data, or None if invalid
    """
    if not isinstance(callback_data, str):
        return None
    
    if not callback_data.startswith(expected_prefix):
        return None
    
    # Extract the ID or value after prefix
    try:
        value = callback_data[len(expected_prefix):]
        # Additional validation can be added here
        return {'value': value, 'prefix': expected_prefix}
    except Exception:
        return None

