from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MatchFeatureSet:
    name: str
    version: str
    feature_columns: tuple[str, ...]
    label_column: str

    @property
    def identifier(
        self,
    ) -> str:
        return (
            f"{self.name}:{self.version}"
        )


BASELINE_WITH_MATCH_SCORE = MatchFeatureSet(
    name="match-ranking-baseline",
    version="v1-with-match-score",
    feature_columns=(
        "skill_score",
        "semantic_score",
        "seniority_score",
        "location_score",
        "matched_skill_count",
        "missing_skill_count",
        "required_skill_count",
        "match_score",
    ),
    label_column="relevance_grade",
)


BASELINE_WITHOUT_MATCH_SCORE = MatchFeatureSet(
    name="match-ranking-baseline",
    version="v1-without-match-score",
    feature_columns=(
        "skill_score",
        "semantic_score",
        "seniority_score",
        "location_score",
        "matched_skill_count",
        "missing_skill_count",
        "required_skill_count",
    ),
    label_column="relevance_grade",
)
LTR_V2 = MatchFeatureSet(
    name="match-ranking-ltr",
    version="v2-cross-encoder",
    feature_columns=(
        "skill_score",
        "semantic_score",
        "reranker_score",
        "seniority_score",
        "location_score",
        "matched_skill_count",
        "missing_skill_count",
        "required_skill_count",
        "skill_match_ratio",
        "missing_skill_ratio",
        "skill_coverage_gap",
    ),
    label_column="relevance_grade",
)

FEATURE_SET_REGISTRY: dict[
    str,
    MatchFeatureSet,
] = {
    BASELINE_WITH_MATCH_SCORE.identifier:
        BASELINE_WITH_MATCH_SCORE,

    BASELINE_WITHOUT_MATCH_SCORE.identifier:
        BASELINE_WITHOUT_MATCH_SCORE,

    LTR_V2.identifier:
        LTR_V2,
}


def get_feature_set(
    identifier: str,
) -> MatchFeatureSet:
    feature_set = FEATURE_SET_REGISTRY.get(
        identifier,
    )

    if feature_set is None:
        supported = ", ".join(
            sorted(
                FEATURE_SET_REGISTRY.keys()
            )
        )

        raise ValueError(
            "Unsupported feature set: "
            f"{identifier}. "
            f"Supported feature sets: {supported}"
        )

    return feature_set

