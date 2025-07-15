from typing import Dict

from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str = "OK"
    services: Dict[str, str] = {}
