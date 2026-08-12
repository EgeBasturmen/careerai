import csv
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from src.domains.matching.ml.feature_sets import (
    MatchFeatureSet,
)

@dataclass(slots=True)
class DatasetValidationIssue:
    severity: str
    code: str
    message: str
    row_number: int | None = None

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DatasetValidationResult:
    dataset_path: str
    is_valid: bool

    row_count: int
    unique_example_count: int
    duplicate_count: int

    label_distribution: dict[str, int]
    missing_value_counts: dict[str, int]

    issues: list[DatasetValidationIssue]

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "dataset_path": self.dataset_path,
            "is_valid": self.is_valid,
            "row_count": self.row_count,
            "unique_example_count": (
                self.unique_example_count
            ),
            "duplicate_count": self.duplicate_count,
            "label_distribution": (
                self.label_distribution
            ),
            "missing_value_counts": (
                self.missing_value_counts
            ),
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
        }


class MatchTrainingDatasetValidator:
    METADATA_COLUMNS = {
        "user_id",
        "resume_id",
        "job_id",
        "algorithm_version",
    }

    PERCENTAGE_SCORE_COLUMNS = {
        "skill_score",
        "semantic_score",
        "reranker_score",
        "seniority_score",
        "location_score",
        "match_score",
    }

    RATIO_COLUMNS = {
        "skill_match_ratio",
        "missing_skill_ratio",
        "skill_coverage_gap",
    }

    COUNT_COLUMNS = {
        "matched_skill_count",
        "missing_skill_count",
        "required_skill_count",
    }

    ID_COLUMNS = {
        "user_id",
        "resume_id",
        "job_id",
    }

    LABEL_COLUMN = "relevance_grade"

    def validate_csv(
        self,
        dataset_path: str,
        feature_set: MatchFeatureSet,
    ) -> DatasetValidationResult:
        path = Path(dataset_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Training dataset not found: "
                f"{dataset_path}"
            )

        rows = self._read_rows(
            path,
        )

        required_columns = {
            *self.METADATA_COLUMNS,
            *feature_set.feature_columns,
            feature_set.label_column,
        }

        issues: list[
            DatasetValidationIssue
        ] = []

        if not rows:
            issues.append(
                DatasetValidationIssue(
                    severity="ERROR",
                    code="EMPTY_DATASET",
                    message=(
                        "The training dataset contains "
                        "no examples."
                    ),
                )
            )

            return DatasetValidationResult(
                dataset_path=dataset_path,
                is_valid=False,
                row_count=0,
                unique_example_count=0,
                duplicate_count=0,
                label_distribution={
                    "0": 0,
                    "1": 0,
                    "2": 0,
                    "3": 0,
                },
                missing_value_counts={},
                issues=issues,
            )

        available_columns = set(
            rows[0].keys()
        )

        missing_columns = (
            required_columns
            - available_columns
        )

        if missing_columns:
            issues.append(
                DatasetValidationIssue(
                    severity="ERROR",
                    code="MISSING_COLUMNS",
                    message=(
                        "Missing required columns: "
                        + ", ".join(
                            sorted(missing_columns)
                        )
                    ),
                )
            )

        missing_value_counts = {
            column: 0
            for column in required_columns
        }

        label_distribution = {
            "0": 0,
            "1": 0,
            "2": 0,
            "3": 0,
        }

        seen_examples: set[
            tuple[int, int, int]
        ] = set()

        duplicate_count = 0

        for row_index, row in enumerate(
            rows,
            start=2,
        ):
            self._validate_missing_values(
                row=row,
                row_number=row_index,
                required_columns=required_columns,
                missing_value_counts=(
                    missing_value_counts
                ),
                issues=issues,
            )

            parsed_ids = self._validate_ids(
                row=row,
                row_number=row_index,
                issues=issues,
            )

            self._validate_scores(
                row=row,
                row_number=row_index,
                feature_set=feature_set,
                issues=issues,
            )

            self._validate_counts(
                row=row,
                row_number=row_index,
                issues=issues,
            )

            label = self._validate_label(
                row=row,
                row_number=row_index,
                issues=issues,
            )

            if label is not None:
                label_distribution[
                    str(label)
                ] += 1

            if parsed_ids is not None:
                if parsed_ids in seen_examples:
                    duplicate_count += 1

                    issues.append(
                        DatasetValidationIssue(
                            severity="WARNING",
                            code=(
                                "DUPLICATE_EXAMPLE"
                            ),
                            message=(
                                "Duplicate user-resume-job "
                                "example detected."
                            ),
                            row_number=row_index,
                        )
                    )
                else:
                    seen_examples.add(
                        parsed_ids
                    )

            self._validate_skill_counts(
                row=row,
                row_number=row_index,
                issues=issues,
            )

            self._validate_algorithm_version(
                row=row,
                row_number=row_index,
                issues=issues,
            )

        self._validate_label_distribution(
            row_count=len(rows),
            label_distribution=(
                label_distribution
            ),
            issues=issues,
        )

        self._validate_dataset_size(
            row_count=len(rows),
            unique_example_count=len(
                seen_examples
            ),
            issues=issues,
        )

        has_error = any(
            issue.severity == "ERROR"
            for issue in issues
        )

        return DatasetValidationResult(
            dataset_path=dataset_path,
            is_valid=not has_error,
            row_count=len(rows),
            unique_example_count=len(
                seen_examples
            ),
            duplicate_count=duplicate_count,
            label_distribution=(
                label_distribution
            ),
            missing_value_counts=(
                missing_value_counts
            ),
            issues=issues,
        )

    def _read_rows(
        self,
        path: Path,
    ) -> list[dict[str, str]]:
        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as input_file:
            reader = csv.DictReader(
                input_file,
            )

            return [
                dict(row)
                for row in reader
            ]

    def _validate_missing_values(
        self,
        row: dict[str, str],
        row_number: int,
        required_columns: set[str],
        missing_value_counts: dict[str, int],
        issues: list[DatasetValidationIssue],
    ) -> None:
        for column in required_columns:
            value = row.get(
                column,
            )

            if value is None or not value.strip():
                missing_value_counts[
                    column
                ] += 1

                issues.append(
                    DatasetValidationIssue(
                        severity="ERROR",
                        code="MISSING_VALUE",
                        message=(
                            f"Missing value for "
                            f"column '{column}'."
                        ),
                        row_number=row_number,
                    )
                )

    def _validate_ids(
        self,
        row: dict[str, str],
        row_number: int,
        issues: list[DatasetValidationIssue],
    ) -> tuple[int, int, int] | None:
        parsed_values: dict[
            str,
            int,
        ] = {}

        for column in self.ID_COLUMNS:
            value = self._parse_int(
                row.get(column),
            )

            if value is None or value <= 0:
                issues.append(
                    DatasetValidationIssue(
                        severity="ERROR",
                        code="INVALID_ID",
                        message=(
                            f"Column '{column}' must "
                            "contain a positive integer."
                        ),
                        row_number=row_number,
                    )
                )

                return None

            parsed_values[column] = value

        return (
            parsed_values["user_id"],
            parsed_values["resume_id"],
            parsed_values["job_id"],
        )

    def _validate_scores(
        self,
        row: dict[str, str],
        row_number: int,
        feature_set: MatchFeatureSet,
        issues: list[DatasetValidationIssue],
    ) -> None:
        selected_features = set(
            feature_set.feature_columns
        )

        percentage_columns = (
            self.PERCENTAGE_SCORE_COLUMNS
            & selected_features
        )

        for column in percentage_columns:
            value = self._parse_float(
                row.get(column),
            )

            if value is None:
                issues.append(
                    DatasetValidationIssue(
                        severity="ERROR",
                        code="INVALID_SCORE",
                        message=(
                            f"Column '{column}' must "
                            "contain a numeric value."
                        ),
                        row_number=row_number,
                    )
                )
                continue

            if not math.isfinite(value):
                issues.append(
                    DatasetValidationIssue(
                        severity="ERROR",
                        code="NON_FINITE_SCORE",
                        message=(
                            f"Column '{column}' contains "
                            "NaN or infinity."
                        ),
                        row_number=row_number,
                    )
                )
                continue

            if not 0.0 <= value <= 100.0:
                issues.append(
                    DatasetValidationIssue(
                        severity="ERROR",
                        code="SCORE_OUT_OF_RANGE",
                        message=(
                            f"Column '{column}' must "
                            "be between 0 and 100."
                        ),
                        row_number=row_number,
                    )
                )

        ratio_columns = (
            self.RATIO_COLUMNS
            & selected_features
        )

        for column in ratio_columns:
            value = self._parse_float(
                row.get(column),
            )

            if value is None:
                issues.append(
                    DatasetValidationIssue(
                        severity="ERROR",
                        code="INVALID_RATIO",
                        message=(
                            f"Column '{column}' must "
                            "contain a numeric value."
                        ),
                        row_number=row_number,
                    )
                )
                continue

            if not math.isfinite(value):
                issues.append(
                    DatasetValidationIssue(
                        severity="ERROR",
                        code="NON_FINITE_RATIO",
                        message=(
                            f"Column '{column}' contains "
                            "NaN or infinity."
                        ),
                        row_number=row_number,
                    )
                )
                continue

            if not 0.0 <= value <= 1.0:
                issues.append(
                    DatasetValidationIssue(
                        severity="ERROR",
                        code="RATIO_OUT_OF_RANGE",
                        message=(
                            f"Column '{column}' must "
                            "be between 0 and 1."
                        ),
                        row_number=row_number,
                    )
                )

    def _validate_counts(
        self,
        row: dict[str, str],
        row_number: int,
        issues: list[DatasetValidationIssue],
    ) -> None:
        for column in self.COUNT_COLUMNS:
            value = self._parse_int(
                row.get(column),
            )

            if value is None or value < 0:
                issues.append(
                    DatasetValidationIssue(
                        severity="ERROR",
                        code="INVALID_COUNT",
                        message=(
                            f"Column '{column}' must "
                            "contain a non-negative "
                            "integer."
                        ),
                        row_number=row_number,
                    )
                )

    def _validate_label(
        self,
        row: dict[str, str],
        row_number: int,
        issues: list[DatasetValidationIssue],
    ) -> int | None:
        value = self._parse_int(
            row.get(
                self.LABEL_COLUMN
            ),
        )

        if value is None or value not in {
            0,
            1,
            2,
            3,
        }:
            issues.append(
                DatasetValidationIssue(
                    severity="ERROR",
                    code="INVALID_LABEL",
                    message=(
                        "relevance_grade must be "
                        "one of 0, 1, 2 or 3."
                    ),
                    row_number=row_number,
                )
            )

            return None

        return value

    def _validate_skill_counts(
        self,
        row: dict[str, str],
        row_number: int,
        issues: list[DatasetValidationIssue],
    ) -> None:
        matched_count = self._parse_int(
            row.get(
                "matched_skill_count"
            ),
        )

        missing_count = self._parse_int(
            row.get(
                "missing_skill_count"
            ),
        )

        required_count = self._parse_int(
            row.get(
                "required_skill_count"
            ),
        )

        if (
            matched_count is None
            or missing_count is None
            or required_count is None
        ):
            return

        calculated_required_count = (
            matched_count
            + missing_count
        )

        if (
            calculated_required_count
            != required_count
        ):
            issues.append(
                DatasetValidationIssue(
                    severity="WARNING",
                    code=(
                        "INCONSISTENT_SKILL_COUNTS"
                    ),
                    message=(
                        "matched_skill_count + "
                        "missing_skill_count does not "
                        "equal required_skill_count."
                    ),
                    row_number=row_number,
                )
            )

    def _validate_algorithm_version(
        self,
        row: dict[str, str],
        row_number: int,
        issues: list[DatasetValidationIssue],
    ) -> None:
        algorithm_version = (
            row.get(
                "algorithm_version",
                "",
            )
            .strip()
        )

        if algorithm_version.lower() in {
            "",
            "unknown",
            "none",
        }:
            issues.append(
                DatasetValidationIssue(
                    severity="WARNING",
                    code=(
                        "UNKNOWN_ALGORITHM_VERSION"
                    ),
                    message=(
                        "algorithm_version is missing "
                        "or unknown."
                    ),
                    row_number=row_number,
                )
            )

    def _validate_label_distribution(
        self,
        row_count: int,
        label_distribution: dict[str, int],
        issues: list[DatasetValidationIssue],
    ) -> None:
        non_empty_labels = [
            label
            for label, count
            in label_distribution.items()
            if count > 0
        ]

        if len(non_empty_labels) <= 1:
            issues.append(
                DatasetValidationIssue(
                    severity="ERROR",
                    code="SINGLE_LABEL_DATASET",
                    message=(
                        "The dataset contains only one "
                        "label class. A supervised model "
                        "cannot learn useful ranking "
                        "behavior from this dataset."
                    ),
                )
            )

        if row_count == 0:
            return

        for label, count in (
            label_distribution.items()
        ):
            ratio = count / row_count

            if count > 0 and ratio < 0.05:
                issues.append(
                    DatasetValidationIssue(
                        severity="WARNING",
                        code="RARE_LABEL",
                        message=(
                            f"Label {label} represents "
                            f"only {ratio:.2%} of the "
                            "dataset."
                        ),
                    )
                )

    def _validate_dataset_size(
        self,
        row_count: int,
        unique_example_count: int,
        issues: list[DatasetValidationIssue],
    ) -> None:
        if unique_example_count < 20:
            issues.append(
                DatasetValidationIssue(
                    severity="WARNING",
                    code="VERY_SMALL_DATASET",
                    message=(
                        "The dataset has fewer than "
                        "20 unique examples. It is only "
                        "suitable for pipeline testing."
                    ),
                )
            )

        elif unique_example_count < 500:
            issues.append(
                DatasetValidationIssue(
                    severity="WARNING",
                    code="SMALL_DATASET",
                    message=(
                        "The dataset has fewer than "
                        "500 unique examples. Model "
                        "metrics will not yet be "
                        "reliable."
                    ),
                )
            )

        duplicate_ratio = (
            1.0
            - (
                unique_example_count
                / row_count
            )
            if row_count > 0
            else 0.0
        )

        if duplicate_ratio > 0.10:
            issues.append(
                DatasetValidationIssue(
                    severity="WARNING",
                    code="HIGH_DUPLICATE_RATIO",
                    message=(
                        "More than 10% of the dataset "
                        "contains duplicate examples."
                    ),
                )
            )

    def _parse_float(
        self,
        value: str | None,
    ) -> float | None:
        if value is None:
            return None

        try:
            return float(
                value.strip()
            )
        except (
            TypeError,
            ValueError,
        ):
            return None

    def _parse_int(
        self,
        value: str | None,
    ) -> int | None:
        if value is None:
            return None

        try:
            return int(
                value.strip()
            )
        except (
            TypeError,
            ValueError,
        ):
            return None