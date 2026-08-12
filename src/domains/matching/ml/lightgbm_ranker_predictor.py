import math
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.domains.matching.ml.ranking_prediction_result import (
    RankedJobPrediction,
    RankingPredictionResult,
)


class LightGBMRankerPredictor:
    def __init__(
        self,
        model_path: str,
    ) -> None:
        self.model_path = model_path

        self.artifact = self._load_artifact(
            model_path,
        )

        self.model = self._get_required_value(
            self.artifact,
            "model",
        )

        self.model_name = str(
            self._get_required_value(
                self.artifact,
                "model_name",
            )
        )

        self.model_version = str(
            self._get_required_value(
                self.artifact,
                "model_version",
            )
        )

        self.feature_set_identifier = str(
            self._get_required_value(
                self.artifact,
                "feature_set_identifier",
            )
        )

        raw_feature_columns = (
            self._get_required_value(
                self.artifact,
                "feature_columns",
            )
        )

        if not isinstance(
            raw_feature_columns,
            list,
        ):
            raise TypeError(
                "Artifact feature_columns "
                "must be a list"
            )

        self.feature_columns = [
            str(column)
            for column
            in raw_feature_columns
        ]

        if not self.feature_columns:
            raise ValueError(
                "Artifact contains no "
                "feature columns"
            )

        self.pipeline_test_only = bool(
            self.artifact.get(
                "pipeline_test_only",
                True,
            )
        )

    def rank(
        self,
        candidates: list[
            dict[str, Any]
        ],
    ) -> RankingPredictionResult:
        if not candidates:
            return RankingPredictionResult(
                model_name=self.model_name,
                model_version=self.model_version,
                feature_set_identifier=(
                    self.feature_set_identifier
                ),
                pipeline_test_only=(
                    self.pipeline_test_only
                ),
                input_count=0,
                predictions=[],
            )

        prepared_candidates: list[
            dict[str, Any]
        ] = []

        feature_rows: list[
            dict[str, float]
        ] = []

        seen_job_ids: set[int] = set()

        for original_rank, candidate in enumerate(
            candidates,
            start=1,
        ):
            job_id = self._parse_job_id(
                candidate.get(
                    "job_id"
                )
            )

            if job_id in seen_job_ids:
                raise ValueError(
                    "Duplicate job_id in ranking "
                    f"candidates: {job_id}"
                )

            seen_job_ids.add(
                job_id
            )

            raw_features = candidate.get(
                "feature_values"
            )

            if not isinstance(
                raw_features,
                dict,
            ):
                raise TypeError(
                    "Each candidate must contain "
                    "a feature_values dictionary"
                )

            normalized_features = (
                self._prepare_features(
                    raw_features
                )
            )

            prepared_candidates.append(
                {
                    "job_id": job_id,
                    "original_rank": (
                        original_rank
                    ),
                    "feature_values": (
                        normalized_features
                    ),
                }
            )

            feature_rows.append(
                normalized_features
            )

        input_dataframe = pd.DataFrame(
            feature_rows,
            columns=self.feature_columns,
        )

        raw_predictions = self.model.predict(
            input_dataframe,
        )

        if (
            len(raw_predictions)
            != len(prepared_candidates)
        ):
            raise ValueError(
                "Model returned an unexpected "
                "number of predictions"
            )

        scored_candidates: list[
            dict[str, Any]
        ] = []

        for candidate, raw_score in zip(
            prepared_candidates,
            raw_predictions,
            strict=True,
        ):
            ranking_score = float(
                raw_score
            )

            if not math.isfinite(
                ranking_score
            ):
                raise ValueError(
                    "Model returned a non-finite "
                    "ranking score"
                )

            scored_candidates.append(
                {
                    **candidate,
                    "ranking_score": (
                        ranking_score
                    ),
                }
            )

        scored_candidates.sort(
            key=lambda item: (
                item["ranking_score"],
                -item["original_rank"],
            ),
            reverse=True,
        )

        predictions = [
            RankedJobPrediction(
                job_id=item["job_id"],
                original_rank=(
                    item["original_rank"]
                ),
                predicted_rank=(
                    predicted_rank
                ),
                ranking_score=(
                    item["ranking_score"]
                ),
                feature_values=(
                    item["feature_values"]
                ),
            )
            for predicted_rank, item
            in enumerate(
                scored_candidates,
                start=1,
            )
        ]

        return RankingPredictionResult(
            model_name=self.model_name,
            model_version=self.model_version,
            feature_set_identifier=(
                self.feature_set_identifier
            ),
            pipeline_test_only=(
                self.pipeline_test_only
            ),
            input_count=len(
                prepared_candidates
            ),
            predictions=predictions,
        )

    def _prepare_features(
        self,
        feature_values: dict[
            str,
            Any,
        ],
    ) -> dict[str, float]:
        missing_features = [
            column
            for column
            in self.feature_columns
            if column
            not in feature_values
        ]

        if missing_features:
            raise ValueError(
                "Missing ranking features: "
                + ", ".join(
                    missing_features
                )
            )

        unexpected_features = (
            set(feature_values)
            - set(self.feature_columns)
        )

        if unexpected_features:
            raise ValueError(
                "Unexpected ranking features: "
                + ", ".join(
                    sorted(
                        unexpected_features
                    )
                )
            )

        normalized_features: dict[
            str,
            float,
        ] = {}

        for column in self.feature_columns:
            raw_value = feature_values[
                column
            ]

            if isinstance(
                raw_value,
                bool,
            ):
                raise TypeError(
                    f"Feature '{column}' "
                    "cannot be boolean"
                )

            try:
                value = float(
                    raw_value
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise TypeError(
                    f"Feature '{column}' "
                    "must be numeric"
                ) from exc

            if not math.isfinite(
                value
            ):
                raise ValueError(
                    f"Feature '{column}' "
                    "must be finite"
                )

            normalized_features[
                column
            ] = value

        return normalized_features

    def _parse_job_id(
        self,
        raw_job_id: Any,
    ) -> int:
        if isinstance(
            raw_job_id,
            bool,
        ):
            raise TypeError(
                "job_id cannot be boolean"
            )

        try:
            job_id = int(
                raw_job_id
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TypeError(
                "job_id must be an integer"
            ) from exc

        if job_id <= 0:
            raise ValueError(
                "job_id must be positive"
            )

        return job_id

    def _load_artifact(
        self,
        model_path: str,
    ) -> dict[str, Any]:
        path = Path(
            model_path,
        )

        if not path.exists():
            raise FileNotFoundError(
                "LightGBM ranker artifact "
                f"not found: {model_path}"
            )

        artifact = joblib.load(
            path,
        )

        if not isinstance(
            artifact,
            dict,
        ):
            raise TypeError(
                "LightGBM ranker artifact "
                "must be a dictionary"
            )

        return artifact

    def _get_required_value(
        self,
        artifact: dict[str, Any],
        key: str,
    ) -> Any:
        if key not in artifact:
            raise ValueError(
                "LightGBM ranker artifact "
                f"is missing key: {key}"
            )

        return artifact[key]