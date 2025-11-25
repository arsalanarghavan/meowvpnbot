import httpx
from core.config import ZARINPAL_MERCHANT_ID, BOT_USERNAME
from core.logger import get_logger
from database.engine import SessionLocal
from database.queries import setting_queries

logger = get_logger(__name__)

# Zarinpal API URLs
ZARINPAL_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZARINPAL_START_PAY_URL = "https://www.zarinpal.com/pg/StartPay/{authority}"


class Zarinpal:
    def __init__(self):
        db = SessionLocal()
        try:
            # Prioritize DB setting, fall back to .env file's value
            self.merchant_id = setting_queries.get_setting(db, 'zarinpal_merchant_id', ZARINPAL_MERCHANT_ID)
        finally:
            db.close()

    async def request_payment(self, amount: int, description: str, transaction_id: int) -> (str, str):
        """
        Requests a new payment from Zarinpal.
        Returns the authority and the payment URL, or (None, None) on failure.
        """
        if not self.merchant_id:
            logger.error("Zarinpal Merchant ID is not configured.")
            return None, None

        # FIX: Dynamically create the callback URL using the bot's username from config
        if not BOT_USERNAME:
            logger.error("Bot username is not configured in .env for Zarinpal callback.")
            return None, None
        callback_url = f"https://t.me/{BOT_USERNAME}?start=verify_{transaction_id}"

        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount * 10, # Convert Toman to Rial
            "description": description,
            "callback_url": callback_url,
            "metadata": {"order_id": str(transaction_id)}
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(ZARINPAL_API_REQUEST, json=payload)
                response.raise_for_status()
                data = response.json().get('data', {})
                errors = response.json().get('errors', [])

                if errors or not data:
                    error_code = errors.get('code', 'Unknown') if errors else 'NoData'
                    logger.error(f"Zarinpal request error: Code {error_code}")
                    return None, None

                authority = data.get('authority')
                if not authority:
                    return None, None

                payment_url = ZARINPAL_START_PAY_URL.format(authority=authority)
                return authority, payment_url
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error during Zarinpal payment request: {e.response.text}")
                return None, None
            except Exception as e:
                logger.error(f"An unexpected error occurred during Zarinpal request: {e}")
                return None, None

    async def verify_payment(self, amount: int, authority: str) -> (bool, str):
        """
        Verifies a payment with Zarinpal.
        Returns the status (True/False) and the reference ID (or error code).
        """
        if not self.merchant_id:
            logger.error("Zarinpal Merchant ID is not configured.")
            return False, "not_configured"

        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount * 10, # Convert Toman to Rial
            "authority": authority
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(ZARINPAL_API_VERIFY, json=payload)
                response.raise_for_status()
                data = response.json().get('data', {})
                errors = response.json().get('errors', [])

                # A successful verification has code 100 or 101 (already verified)
                if data and data.get('code') in [100, 101]:
                    ref_id = data.get('ref_id')
                    return True, str(ref_id)
                else:
                    error_code = errors.get('code', data.get('code', 'Unknown')) if (errors or data) else "Unknown"
                    logger.error(f"Zarinpal verification error: Code {error_code}")
                    return False, str(error_code)

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error during Zarinpal payment verification: {e.response.text}")
                return False, "http_error"
            except Exception as e:
                logger.error(f"An unexpected error occurred during Zarinpal verification: {e}")
                return False, "unexpected_error"