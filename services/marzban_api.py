import httpx
import uuid
from datetime import datetime, timedelta
from core.config import MARZBAN_API_BASE_URL, MARZBAN_API_USERNAME, MARZBAN_API_PASSWORD
from database.models.plan import Plan
from database.models.service import Service

class MarzbanAPI:
    def __init__(self):
        self.base_url = MARZBAN_API_BASE_URL
        self.username = MARZBAN_API_USERNAME
        self.password = MARZBAN_API_PASSWORD
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
            print(f"Failed to log into Marzban: {e}")
            raise

    async def create_user(self, plan: Plan, prefix: str = "user"):
        """Creates a new user in Marzban based on a plan."""
        await self._login()
        
        username = f"{prefix}-{uuid.uuid4().hex[:8]}"
        
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
            print(f"Failed to create user in Marzban: {e.json()}")
            raise

    async def get_user(self, username: str):
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

    async def renew_user(self, service: Service):
        """Renews a user in Marzban by extending expire date and adding traffic."""
        await self._login()

        username = service.username_in_panel
        plan = service.plan
        panel_user = await self.get_user(username)
        if not panel_user:
            raise Exception(f"User {username} not found in Marzban panel.")

        now_ts = int(datetime.utcnow().timestamp())
        current_expire_ts = panel_user.get('expire') or now_ts
        start_ts = current_expire_ts if current_expire_ts > now_ts else now_ts
        new_expire_date = datetime.fromtimestamp(start_ts) + timedelta(days=plan.duration_days)
        new_expire_timestamp = int(new_expire_date.timestamp())

        current_data_limit = panel_user.get('data_limit', 0)
        new_traffic_bytes = (plan.traffic_gb * 1024 * 1024 * 1024) if plan.traffic_gb > 0 else 0
        new_data_limit = current_data_limit + new_traffic_bytes

        update_data = {
            "expire": new_expire_timestamp,
            "data_limit": new_data_limit,
            "status": "active"
        }

        try:
            response = await self.client.put(f"/api/user/{username}", json=update_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to renew user {username} in Marzban: {e.json()}")
            raise

    async def reset_user_uuid(self, username: str):
        """Resets the UUIDs for a user's proxies."""
        await self._login()
        try:
            user_details = await self.get_user(username)
            if not user_details:
                return None
            
            current_proxies = user_details.get('proxies', {})
            new_proxies = {}
            if 'vmess' in current_proxies:
                new_proxies['vmess'] = {}
            if 'vless' in current_proxies:
                new_proxies['vless'] = {}

            response = await self.client.put(f"/api/user/{username}", json={"proxies": new_proxies})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to reset UUID for {username}: {e.json()}")
            raise
            
    async def deactivate_user(self, username: str):
        """Deactivates a user in Marzban by setting their status to 'disabled'."""
        await self._login()
        update_data = {"status": "disabled"}
        try:
            response = await self.client.put(f"/api/user/{username}", json=update_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to deactivate user {username} in Marzban: {e.json()}")
            raise

    async def get_all_users_from_panel(self):
        """Retrieves all users from the Marzban panel."""
        await self._login()
        try:
            response = await self.client.get("/api/users")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to get all users from panel: {e.json()}")
            raise

    async def get_system_stats(self):
        """Retrieves system stats from Marzban."""
        await self._login()
        try:
            response = await self.client.get("/api/system")
            response.raise_for_status()
            return response.json().get('stats', {})
        except httpx.HTTPStatusError as e:
            print(f"Failed to get system stats: {e.json()}")
            raise