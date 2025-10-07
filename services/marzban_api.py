import httpx
import uuid
import base64
from datetime import datetime, timedelta
from typing import List, Optional

from database.models.plan import Plan
from database.models.service import Service
from database.models.panel import Panel

class MarzbanAPI:
    def __init__(self, panel: Panel):
        """Initializes the API with credentials from a Panel object."""
        self.base_url = panel.api_base_url
        self.username = panel.username
        self.password = panel.password
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=20.0)
        self.access_token = None

    async def _login(self):
        """Logs into Marzban to get an access token."""
        if self.access_token:
            return
        try:
            response = await self.client.post(
                "/api/admin/token",
                data={"username": self.username, "password": self.password}
            )
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
            self.client.headers["Authorization"] = f"Bearer {self.access_token}"
        except httpx.HTTPStatusError as e:
            print(f"Failed to log into Marzban panel {self.base_url}: {e}")
            raise

    async def create_user(self, plan: Plan, username: str):
        """Creates a new user in Marzban with a specific username."""
        await self._login()
        
        expire_date = datetime.utcnow() + timedelta(days=plan.duration_days)
        expire_timestamp = int(expire_date.timestamp())
        
        data_limit = plan.traffic_gb * 1024 * 1024 * 1024 if plan.traffic_gb > 0 else 0
        
        user_data = {
            "username": username,
            "proxies": {"vmess": {}, "vless": {}},
            "expire": expire_timestamp,
            "data_limit": data_limit,
            "data_limit_reset_strategy": "no_reset",
            "ip_limit": plan.device_limit,
            "status": "active"
        }
        
        try:
            response = await self.client.post("/api/user", json=user_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                print(f"User {username} already exists on panel {self.base_url}. Fetching data.")
                return await self.get_user(username)
            print(f"Failed to create user {username} in Marzban: {e.json()}")
            raise

    async def get_user(self, username: str) -> Optional[dict]:
        """Retrieves a user's details from Marzban."""
        await self._login()
        try:
            response = await self.client.get(f"/api/user/{username}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            print(f"Failed to get user {username}: {e.json()}")
            raise

    async def renew_user(self, service: Service) -> Optional[dict]:
        """Renews a user's subscription in Marzban."""
        await self._login()
        
        panel_user = await self.get_user(service.username_in_panel)
        if not panel_user:
            return None # User does not exist on this panel

        current_expire_ts = panel_user.get('expire', 0)
        now_ts = int(datetime.utcnow().timestamp())
        
        # If the subscription is already expired, renew from now. Otherwise, extend the current expiry date.
        start_date = datetime.utcfromtimestamp(current_expire_ts) if current_expire_ts > now_ts else datetime.utcnow()
        
        new_expire_date = start_date + timedelta(days=service.plan.duration_days)
        new_expire_ts = int(new_expire_date.timestamp())

        # Also, reset traffic if the plan has a data limit
        new_data_limit = panel_user.get('data_limit', 0)
        if service.plan.traffic_gb > 0:
            new_data_limit += service.plan.traffic_gb * 1024 * 1024 * 1024
        
        update_data = {
            "expire": new_expire_ts,
            "data_limit": new_data_limit,
            "status": "active" # Ensure the user is active
        }
        
        try:
            response = await self.client.put(f"/api/user/{service.username_in_panel}", json=update_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to renew user {service.username_in_panel} in Marzban: {e.json()}")
            raise

    async def deactivate_user(self, username: str):
        """Deactivates a user in Marzban."""
        await self._login()
        try:
            # We modify the user to set their status to "disabled"
            response = await self.client.put(f"/api/user/{username}", json={"status": "disabled"})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to deactivate user {username} in Marzban: {e.json()}")
            raise
    
    async def reset_user_uuid(self, username: str):
        """Resets a user's UUIDs by regenerating proxies."""
        await self._login()
        try:
            response = await self.client.post(f"/api/user/{username}/reset")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to reset user UUID for {username}: {e.json()}")
            raise

    @staticmethod
    async def get_combined_subscription_link(user_details_list: List[dict]) -> str:
        """
        Combines configs from multiple panels into a single subscription link.
        """
        all_configs = []
        for user_details in user_details_list:
            if not user_details or 'subscription_url' not in user_details or not user_details['subscription_url']:
                continue
            
            sub_url = user_details['subscription_url']
            try:
                base64_part = sub_url.split('/')[-1].split('?')[0]
                decoded_configs = base64.urlsafe_b64decode(base64_part + '==').decode('utf-8')
                all_configs.append(decoded_configs.strip())
            except Exception as e:
                print(f"Could not decode subscription url {sub_url}: {e}")
                continue
        
        if not all_configs:
            return "لینک اشتراکی یافت نشد."

        combined_configs = "\n".join(all_configs)
        encoded_combined_configs = base64.urlsafe_b64encode(combined_configs.encode('utf-8')).decode('utf-8').rstrip('=')
        
        # A more generic approach might be better, but vmess is common
        return f"vmess://{encoded_combined_configs}"