from dataclasses import asdict, dataclass


@dataclass(slots=True)
class MatchTrainingExample:
    user_id: int
    resume_id: int
    job_id: int

    algorithm_version: str

    skill_score: float
    semantic_score: float
    reranker_score: float
    seniority_score: float
    location_score: float

    matched_skill_count: int
    missing_skill_count: int
    required_skill_count: int
    skill_match_ratio: float
    missing_skill_ratio: float
    skill_coverage_gap: float

    match_score: float

    relevance_grade: int

    def to_dict(
        self,
    ) -> dict:
        return asdict(self)