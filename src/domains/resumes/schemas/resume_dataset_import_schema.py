from pydantic import BaseModel


class ResumeDatasetImportResult(BaseModel):
    dataset_name: str
    source: str
    user_id: int

    discovered_count: int
    imported_count: int
    skipped_count: int
    failed_count: int

    resume_ids: list[int]
    errors: list[str]