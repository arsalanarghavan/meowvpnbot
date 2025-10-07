import httpx
from core.config import ZARINPAL_MERCHANT_ID, BOT_USERNAME

# Zarinpal API URLs
ZARINPAL_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZARINPAL_START_PAY_URL = "https://www.zarinpal.com/pg/StartPay/{authority}"


class Zarinpal:
    def __init__(self):
        self.merchant_id = ZARINPAL_MERCHANT_ID

    async def request_payment(self, amount: int, description: str, transaction_id: int) -> (str, str):
        """
        Requests a new payment from Zarinpal.
        Returns the authority and the payment URL.
        """
        # The callback URL will point back to the bot with the transaction ID
        callback_url = f"https://t.me/{BOT_USERNAME}?start=verify_{transaction_id}"
        
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "description": description,
            "callback_url": callback_url,
            "metadata": {"order_id": str(transaction_id)}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(ZARINPAL_API_REQUEST, json=payload)
                response.raise_for_status()
                data = response.json().get('data', {})
                errors = response.json().get('errors', [])
                
                if errors:
                    error_code = errors.get('code', 'Unknown')
                    print(f"Zarinpal request error: {error_code}")
                    return None, None

                authority = data.get('authority')
                payment_url = ZARINPAL_START_PAY_URL.format(authority=authority)
                return authority, payment_url
            except httpx.HTTPStatusError as e:
                print(f"HTTP error during Zarinpal payment request: {e}")
                return None, None
            except Exception as e:
                print(f"An unexpected error occurred during Zarinpal request: {e}")
                return None, None

    async def verify_payment(self, amount: int, authority: str) -> (bool, str):
        """
        Verifies a payment with Zarinpal.
        Returns the status (True/False) and the reference ID.
        """
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "authority": authority
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(ZARINPAL_API_VERIFY, json=payload)
                response.raise_for_status()
                data = response.json().get('data', {})
                errors = response.json().get('errors', [])

                if errors or not data or data.get('code') != 100:
                    error_code = errors.get('code', data.get('code', 'Unknown')) if (errors or data) else "Unknown"
                    print(f"Zarinpal verification error: {error_code}")
                    return False, str(error_code)

                ref_id = data.get('ref_id')
                return True, str(ref_id)
            except httpx.HTTPStatusError as e:
                print(f"HTTP error during Zarinpal payment verification: {e}")
                return False, "http_error"
            except Exception as e:
                print(f"An unexpected error occurred during Zarinpal verification: {e}")
                return False, "unexpected_error"