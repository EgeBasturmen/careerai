from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.domains.matching.ml.prediction_result import (
    MatchModelPredictionResult,
)


class MatchModelPredictor:
    MIN_RELEVANCE = 0.0
    MAX_RELEVANCE = 3.0

    def __init__(
        self,
        model_path: str,
    ):
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
                "Artifact feature_columns must "
                "be a list"
            )

        self.feature_columns = [
            str(column)
            for column in raw_feature_columns
        ]

        if not self.feature_columns:
            raise ValueError(
                "Artifact contains no feature columns"
            )

    def predict(
        self,
        feature_values: dict[str, float | int],
    ) -> MatchModelPredictionResult:
        normalized_features = (
            self._prepare_features(
                feature_values,
            )
        )

        input_dataframe = pd.DataFrame(
            [
                normalized_features,
            ],
            columns=self.feature_columns,
        )

        predictions = self.model.predict(
            input_dataframe,
        )

        if len(predictions) != 1:
            raise ValueError(
                "Model returned an unexpected "
                "number of predictions"
            )

        raw_prediction = float(
            predictions[0]
        )

        predicted_relevance = self._clamp(
            raw_prediction,
        )

        predicted_grade = int(
            round(
                predicted_relevance,
            )
        )

        return MatchModelPredictionResult(
            model_name=self.model_name,
            model_version=self.model_version,
            feature_set_identifier=(
                self.feature_set_identifier
            ),
            raw_prediction=raw_prediction,
            predicted_relevance=(
                predicted_relevance
            ),
            predicted_grade=predicted_grade,
            feature_values=normalized_features,
        )

    def _prepare_features(
        self,
        feature_values: dict[str, float | int],
    ) -> dict[str, float]:
        missing_features = [
            column
            for column in self.feature_columns
            if column not in feature_values
        ]

        if missing_features:
            raise ValueError(
                "Missing prediction features: "
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
                "Unexpected prediction features: "
                + ", ".join(
                    sorted(
                        unexpected_features
                    )
                )
            )

        normalized_features: dict[str, float] = {}

        for column in self.feature_columns:
            value = feature_values[column]

            if isinstance(value, bool):
                raise TypeError(
                    f"Feature '{column}' cannot "
                    "be boolean"
                )

            try:
                normalized_features[column] = float(
                    value
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise TypeError(
                    f"Feature '{column}' must "
                    "be numeric"
                ) from exc

        return normalized_features

    def _load_artifact(
        self,
        model_path: str,
    ) -> dict[str, Any]:
        path = Path(
            model_path,
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Model artifact not found: "
                f"{model_path}"
            )

        artifact = joblib.load(
            path,
        )

        if not isinstance(
            artifact,
            dict,
        ):
            raise TypeError(
                "Model artifact must be a dictionary"
            )

        return artifact

    def _get_required_value(
        self,
        artifact: dict[str, Any],
        key: str,
    ) -> Any:
        if key not in artifact:
            raise ValueError(
                f"Model artifact is missing "
                f"required key: {key}"
            )

        return artifact[key]

    def _clamp(
        self,
        value: float,
    ) -> float:
        return max(
            self.MIN_RELEVANCE,
            min(
                value,
                self.MAX_RELEVANCE,
            ),
        )