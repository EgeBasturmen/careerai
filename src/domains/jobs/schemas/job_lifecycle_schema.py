from pydantic import BaseModel


class JobLifecycleResult(BaseModel):
    stale_days: int
    deactivated_count: int