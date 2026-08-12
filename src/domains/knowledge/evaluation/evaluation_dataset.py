from pydantic import BaseModel

from src.domains.knowledge.evaluation.evaluation_case import (
    EvaluationCase,
)


class EvaluationDataset(BaseModel):
    dataset_name: str

    version: str

    cases: list[EvaluationCase]