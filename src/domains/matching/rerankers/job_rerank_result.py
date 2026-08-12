from dataclasses import dataclass

from src.domains.jobs.models.job import Job


@dataclass(slots=True)
class JobRerankResult:
    job: Job

    semantic_score: float

    reranker_score: float

    original_rank: int