"""
Audit logging for sensitive operations.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from core.logger import get_logger
from database.engine import SessionLocal

logger = get_logger(__name__)


def log_admin_action(
    admin_id: int,
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Logs an admin action for audit purposes.
    
    Args:
        admin_id: ID of the admin performing the action
        action: Action name (e.g., 'user_blocked', 'balance_added', 'plan_created')
        target_type: Type of target (e.g., 'user', 'plan', 'transaction')
        target_id: ID of the target
        details: Additional details as dictionary
    """
    try:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'admin_id': admin_id,
            'action': action,
            'target_type': target_type,
            'target_id': target_id,
            'details': details or {}
        }
        
        # Log to file
        logger.info(f"AUDIT: Admin {admin_id} performed {action} on {target_type} {target_id}", extra=log_entry)
        
        # Optionally log to database (if audit_log table exists)
        # db = SessionLocal()
        # try:
        #     # Insert into audit_log table
        #     pass
        # finally:
        #     db.close()
            
    except Exception as e:
        logger.error(f"Failed to log admin action: {e}", exc_info=True)


def log_payment_action(
    user_id: int,
    action: str,
    transaction_id: Optional[int] = None,
    amount: Optional[int] = None,
    payment_method: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Logs a payment-related action for audit purposes.
    
    Args:
        user_id: ID of the user
        action: Action name (e.g., 'payment_initiated', 'payment_completed', 'payment_failed')
        transaction_id: Transaction ID
        amount: Payment amount
        payment_method: Payment method used
        details: Additional details
    """
    try:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'transaction_id': transaction_id,
            'amount': amount,
            'payment_method': payment_method,
            'details': details or {}
        }
        
        logger.info(f"AUDIT: Payment {action} for user {user_id}, tx_id: {transaction_id}, amount: {amount}", extra=log_entry)
        
    except Exception as e:
        logger.error(f"Failed to log payment action: {e}", exc_info=True)


def log_login_attempt(
    user_id: Optional[int],
    username: Optional[str],
    success: bool,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> None:
    """
    Logs a login attempt for audit purposes.
    
    Args:
        user_id: ID of the user (if successful)
        username: Username attempted
        success: Whether login was successful
        ip_address: IP address of the request
        user_agent: User agent string
    """
    try:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'username': username,
            'success': success,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"AUDIT: Login {status} for user {user_id or username} from {ip_address}", extra=log_entry)
        
    except Exception as e:
        logger.error(f"Failed to log login attempt: {e}", exc_info=True)


def log_service_action(
    user_id: int,
    action: str,
    service_id: Optional[int] = None,
    plan_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Logs a service-related action for audit purposes.
    
    Args:
        user_id: ID of the user
        action: Action name (e.g., 'service_created', 'service_renewed', 'service_cancelled')
        service_id: Service ID
        plan_id: Plan ID
        details: Additional details
    """
    try:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'service_id': service_id,
            'plan_id': plan_id,
            'details': details or {}
        }
        
        logger.info(f"AUDIT: Service {action} for user {user_id}, service_id: {service_id}", extra=log_entry)
        
    except Exception as e:
        logger.error(f"Failed to log service action: {e}", exc_info=True)

