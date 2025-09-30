import httpx
import uuid
from datetime import datetime, timedelta
from core.config import MARZBAN_API_BASE_URL, MARZBAN_API_USERNAME, MARZBAN_API_PASSWORD
from database.models.plan import Plan

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