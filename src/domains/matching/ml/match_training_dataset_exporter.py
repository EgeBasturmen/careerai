import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from src.domains.matching.ml.feature_sets import (
    MatchFeatureSet,
)
from src.domains.matching.ml.match_feature_extractor import (
    MatchFeatureExtractor,
)
from src.domains.matching.ml.match_training_example import (
    MatchTrainingExample,
)
from src.domains.matching.repositories.match_training_repository import (
    MatchTrainingRepository,
)


class MatchTrainingDatasetExporter:
    METADATA_COLUMNS = (
        "user_id",
        "resume_id",
        "job_id",
        "algorithm_version",
    )

    def __init__(
        self,
        db: Session,
    ):
        self.repository = MatchTrainingRepository(
            db,
        )

        self.feature_extractor = (
            MatchFeatureExtractor()
        )

    def export_csv(
        self,
        output_path: str,
        dataset_name: str,
        dataset_version: str,
        feature_set: MatchFeatureSet,
        algorithm_version: str | None = None,
    ) -> dict[str, Any]:
        examples = self._build_examples(
            algorithm_version=algorithm_version,
        )

        path = Path(
            output_path,
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        fieldnames = self._build_selected_columns(
            feature_set=feature_set,
        )

        rows = [
            self._filter_example_columns(
                example=example,
                selected_columns=fieldnames,
            )
            for example in examples
        ]

        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as output_file:
            writer = csv.DictWriter(
                output_file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            writer.writerows(
                rows,
            )

        return self._build_metadata(
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            algorithm_version=algorithm_version,
            output_path=output_path,
            output_format="csv",
            feature_set=feature_set,
            examples=examples,
        )

    def export_jsonl(
        self,
        output_path: str,
        dataset_name: str,
        dataset_version: str,
        feature_set: MatchFeatureSet,
        algorithm_version: str | None = None,
    ) -> dict[str, Any]:
        examples = self._build_examples(
            algorithm_version=algorithm_version,
        )

        path = Path(
            output_path,
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        selected_columns = self._build_selected_columns(
            feature_set=feature_set,
        )

        lines = [
            json.dumps(
                self._filter_example_columns(
                    example=example,
                    selected_columns=selected_columns,
                ),
                ensure_ascii=False,
            )
            for example in examples
        ]

        path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return self._build_metadata(
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            algorithm_version=algorithm_version,
            output_path=output_path,
            output_format="jsonl",
            feature_set=feature_set,
            examples=examples,
        )

    def _build_examples(
        self,
        algorithm_version: str | None,
    ) -> list[MatchTrainingExample]:
        rows = (
            self.repository.list_labeled_matches(
                algorithm_version=algorithm_version,
            )
        )

        return [
            self.feature_extractor.extract(
                match=match,
                feedback=feedback,
            )
            for match, feedback in rows
        ]

    def _build_selected_columns(
        self,
        feature_set: MatchFeatureSet,
    ) -> list[str]:
        return [
            *self.METADATA_COLUMNS,
            *feature_set.feature_columns,
            feature_set.label_column,
        ]

    def _filter_example_columns(
        self,
        example: MatchTrainingExample,
        selected_columns: list[str],
    ) -> dict[str, Any]:
        raw_row = example.to_dict()

        return {
            column: raw_row.get(
                column,
            )
            for column in selected_columns
        }

    def _build_metadata(
        self,
        dataset_name: str,
        dataset_version: str,
        algorithm_version: str | None,
        output_path: str,
        output_format: str,
        feature_set: MatchFeatureSet,
        examples: list[MatchTrainingExample],
    ) -> dict[str, Any]:
        label_distribution = {
            "0": 0,
            "1": 0,
            "2": 0,
            "3": 0,
        }

        for example in examples:
            label = str(
                example.relevance_grade
            )

            label_distribution[label] = (
                label_distribution.get(
                    label,
                    0,
                )
                + 1
            )

        return {
            "dataset_name": dataset_name,
            "dataset_version": dataset_version,
            "algorithm_version": (
                algorithm_version
            ),
            "feature_set": (
                feature_set.identifier
            ),
            "feature_columns": list(
                feature_set.feature_columns
            ),
            "label_column": (
                feature_set.label_column
            ),
            "generated_at": datetime.now(
                timezone.utc,
            ).isoformat(),
            "output_path": output_path,
            "output_format": output_format,
            "example_count": len(
                examples
            ),
            "label_distribution": (
                label_distribution
            ),
        }