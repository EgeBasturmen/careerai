from pydantic import BaseModel


class EvaluationReport(BaseModel):
    dataset_name: str

    version: str

    case_count: int

    mean_precision_at_k: float

    mean_recall_at_k: float

    mean_mrr: float

    mean_ndcg_at_k: float