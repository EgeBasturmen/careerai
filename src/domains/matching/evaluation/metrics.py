import math


class RankingMetrics:
    def precision_at_k(
        self,
        predicted_job_ids: list[int],
        relevant_job_ids: set[int],
        k: int,
    ) -> float:
        self._validate_k(k)

        top_k = predicted_job_ids[:k]

        if not top_k:
            return 0.0

        relevant_count = sum(
            1
            for job_id in top_k
            if job_id in relevant_job_ids
        )

        return relevant_count / len(top_k)

    def recall_at_k(
        self,
        predicted_job_ids: list[int],
        relevant_job_ids: set[int],
        k: int,
    ) -> float:
        self._validate_k(k)

        if not relevant_job_ids:
            return 0.0

        top_k = predicted_job_ids[:k]

        relevant_count = sum(
            1
            for job_id in top_k
            if job_id in relevant_job_ids
        )

        return (
            relevant_count
            / len(relevant_job_ids)
        )

    def reciprocal_rank(
        self,
        predicted_job_ids: list[int],
        relevant_job_ids: set[int],
    ) -> float:
        for rank, job_id in enumerate(
            predicted_job_ids,
            start=1,
        ):
            if job_id in relevant_job_ids:
                return 1.0 / rank

        return 0.0

    def ndcg_at_k(
        self,
        predicted_job_ids: list[int],
        relevance_grades: dict[int, int],
        k: int,
    ) -> float:
        self._validate_k(k)

        top_k = predicted_job_ids[:k]

        dcg = self._discounted_cumulative_gain(
            job_ids=top_k,
            relevance_grades=relevance_grades,
        )

        ideal_grades = sorted(
            relevance_grades.values(),
            reverse=True,
        )[:k]

        ideal_dcg = sum(
            self._gain(grade)
            / math.log2(index + 2)
            for index, grade in enumerate(
                ideal_grades
            )
        )

        if ideal_dcg == 0:
            return 0.0

        return dcg / ideal_dcg

    def _discounted_cumulative_gain(
        self,
        job_ids: list[int],
        relevance_grades: dict[int, int],
    ) -> float:
        return sum(
            self._gain(
                relevance_grades.get(
                    job_id,
                    0,
                )
            )
            / math.log2(index + 2)
            for index, job_id in enumerate(
                job_ids
            )
        )

    def _gain(
        self,
        relevance_grade: int,
    ) -> float:
        return (
            2 ** relevance_grade
        ) - 1

    def _validate_k(
        self,
        k: int,
    ) -> None:
        if k <= 0:
            raise ValueError(
                "k must be greater than zero"
            )