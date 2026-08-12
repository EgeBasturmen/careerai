import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class MatchingEvaluationCase:
    name: str
    user_id: int
    resume_id: int
    relevance_grades: dict[int, int]


@dataclass(slots=True)
class MatchingEvaluationDataset:
    dataset_name: str
    dataset_version: str
    cases: list[MatchingEvaluationCase]


class MatchingEvaluationDatasetLoader:
    def load(
        self,
        dataset_path: str,
    ) -> MatchingEvaluationDataset:
        path = Path(dataset_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Evaluation dataset not found: {dataset_path}"
            )

        raw_data = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

        raw_cases = raw_data.get(
            "cases",
            [],
        )

        cases = [
            MatchingEvaluationCase(
                name=raw_case["name"],
                user_id=int(
                    raw_case["user_id"]
                ),
                resume_id=int(
                    raw_case["resume_id"]
                ),
                relevance_grades={
                    int(job_id): int(grade)
                    for job_id, grade
                    in raw_case[
                        "relevance_grades"
                    ].items()
                },
            )
            for raw_case in raw_cases
        ]

        return MatchingEvaluationDataset(
            dataset_name=raw_data[
                "dataset_name"
            ],
            dataset_version=raw_data[
                "dataset_version"
            ],
            cases=cases,
        )