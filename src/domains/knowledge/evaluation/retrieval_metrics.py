from dataclasses import dataclass


@dataclass(slots=True)
class RetrievalMetrics:
    precision_at_k: float

    recall_at_k: float

    mrr: float

    ndcg_at_k: float

    retrieved_count: int

    relevant_count: int

    relevant_retrieved_count: int