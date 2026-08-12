from datetime import datetime

from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    storage_path: str
    status: str
    created_at: datetime
    raw_text: str | None
    parsed_profile: dict | None

    model_config = {
        "from_attributes": True,
    }