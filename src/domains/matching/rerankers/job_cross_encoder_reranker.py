from src.domains.jobs.models.job import Job
from src.domains.matching.rerankers.job_rerank_result import (
    JobRerankResult,
)
from src.infrastructure.reranking.cross_encoder_scorer import (
    CrossEncoderScorer,
)


class JobCrossEncoderReranker:
    def __init__(
        self,
        *,
        model_name: str,
        batch_size: int = 16,
    ) -> None:
        self.scorer = CrossEncoderScorer(
            model_name=model_name,
            batch_size=batch_size,
        )

    def rerank(
        self,
        *,
        query_text: str,
        jobs: list[tuple[Job, float]],
        limit: int,
        minimum_score: float = 0.0,
    ) -> list[JobRerankResult]:
        normalized_query = query_text.strip()

        if not normalized_query:
            raise ValueError(
                "Query cannot be empty"
            )

        if limit < 1:
            raise ValueError(
                "Limit must be positive"
            )

        if not jobs:
            return []

        passages = [
            self._build_passage(job)
            for job, _ in jobs
        ]

        scores = self.scorer.score(
            query_text=normalized_query,
            passages=passages,
        )

        reranked: list[JobRerankResult] = []

        for rank, (
            (job, semantic_score),
            reranker_score,
        ) in enumerate(
            zip(
                jobs,
                scores,
                strict=True,
            ),
            start=1,
        ):
            if reranker_score < minimum_score:
                continue

            reranked.append(
                JobRerankResult(
                    job=job,
                    semantic_score=semantic_score,
                    reranker_score=float(
                        reranker_score
                    ),
                    original_rank=rank,
                )
            )

        reranked.sort(
            key=lambda item: (
                item.reranker_score,
                -item.original_rank,
            ),
            reverse=True,
        )

        return reranked[:limit]

    def _build_passage(
        self,
        job: Job,
    ) -> str:
        sections: list[str] = []

        if job.title:
            sections.append(job.title)

        if job.company_name:
            sections.append(job.company_name)

        if job.location:
            sections.append(job.location)

        if job.description:
            sections.append(job.description)

        if job.required_skills:
            sections.extend(
                job.required_skills
            )

        return "\n".join(
            sections
        )