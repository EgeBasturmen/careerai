from pydantic import BaseModel, Field


class EvaluationCase(BaseModel):
    case_id: str

    query: str

    expected_document_ids: list[int] = Field(
        min_length=1,
    )

    category: str | None = None

    language: str | None = None