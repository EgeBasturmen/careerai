import json
import math
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import (
    RandomForestRegressor,
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import (
    train_test_split,
)

from src.domains.matching.ml.feature_sets import (
    get_feature_set,
)
from src.domains.matching.ml.training_dataset_manifest import (
    TrainingDatasetManifest,
)
from src.domains.matching.ml.training_result import (
    MatchModelTrainingResult,
)


class BaselineMatchModelTrainer:
    def train(
        self,
        dataset_path: str,
        manifest_path: str,
        model_output_path: str,
        report_output_path: str,
        model_name: str = "random-forest-regressor",
        model_version: str = "v1",
        random_state: int = 42,
    ) -> MatchModelTrainingResult:
        manifest = self._load_manifest(
            manifest_path,
        )

        feature_set_identifier = (
            f"{manifest.feature_set_name}:"
            f"{manifest.feature_set_version}"
        )

        feature_set = get_feature_set(
            feature_set_identifier,
        )

        dataframe = pd.read_csv(
            dataset_path,
        )

        if dataframe.empty:
            raise ValueError(
                "Training dataset is empty"
            )

        missing_columns = (
            set(feature_set.feature_columns)
            | {feature_set.label_column}
        ) - set(dataframe.columns)

        if missing_columns:
            raise ValueError(
                "Training dataset is missing columns: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        x = dataframe[
            list(
                feature_set.feature_columns
            )
        ].astype(float)

        y = dataframe[
            feature_set.label_column
        ].astype(float)

        row_count = len(dataframe)

        if row_count < 2:
            raise ValueError(
                "At least 2 rows are required "
                "to test the training pipeline"
            )

        if row_count >= 5:
            x_train, x_test, y_train, y_test = (
                train_test_split(
                    x,
                    y,
                    test_size=0.20,
                    random_state=random_state,
                )
            )
        else:
            x_train = x
            y_train = y
            x_test = x
            y_test = y

        model = RandomForestRegressor(
            n_estimators=100,
            random_state=random_state,
            min_samples_leaf=1,
        )

        model.fit(
            x_train,
            y_train,
        )

        predictions = model.predict(
            x_test,
        )

        mae = mean_absolute_error(
            y_test,
            predictions,
        )

        rmse = math.sqrt(
            mean_squared_error(
                y_test,
                predictions,
            )
        )

        calculated_r2: float | None = None

        if len(y_test) >= 2:
            calculated_r2 = r2_score(
                y_test,
                predictions,
            )

        model_path = Path(
            model_output_path,
        )

        model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        artifact = {
            "model": model,
            "model_name": model_name,
            "model_version": model_version,
            "feature_set_identifier": (
                feature_set_identifier
            ),
            "feature_columns": list(
                feature_set.feature_columns
            ),
            "label_column": (
                feature_set.label_column
            ),
            "dataset_sha256": (
                manifest.dataset_sha256
            ),
        }

        joblib.dump(
            artifact,
            model_path,
        )

        report = {
            "model_name": model_name,
            "model_version": model_version,
            "dataset_path": dataset_path,
            "manifest_path": manifest_path,
            "dataset_sha256": (
                manifest.dataset_sha256
            ),
            "feature_set_identifier": (
                feature_set_identifier
            ),
            "feature_columns": list(
                feature_set.feature_columns
            ),
            "row_count": row_count,
            "train_row_count": len(
                x_train
            ),
            "test_row_count": len(
                x_test
            ),
            "metrics": {
                "mean_absolute_error": (
                    float(mae)
                ),
                "root_mean_squared_error": (
                    float(rmse)
                ),
                "r2_score": (
                    float(calculated_r2)
                    if calculated_r2 is not None
                    else None
                ),
            },
            "warning": (
                "This model is only for pipeline "
                "testing and must not be used in "
                "production with the current dataset."
            ),
        }

        report_path = Path(
            report_output_path,
        )

        report_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        report_path.write_text(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return MatchModelTrainingResult(
            model_name=model_name,
            model_version=model_version,
            dataset_path=dataset_path,
            manifest_path=manifest_path,
            feature_set_identifier=(
                feature_set_identifier
            ),
            row_count=row_count,
            train_row_count=len(
                x_train
            ),
            test_row_count=len(
                x_test
            ),
            mean_absolute_error=float(
                mae
            ),
            root_mean_squared_error=float(
                rmse
            ),
            r2_score=(
                float(calculated_r2)
                if calculated_r2 is not None
                else None
            ),
            model_path=str(
                model_path
            ),
            report_path=str(
                report_path
            ),
        )

    def _load_manifest(
        self,
        manifest_path: str,
    ) -> TrainingDatasetManifest:
        path = Path(
            manifest_path,
        )

        if not path.exists():
            raise FileNotFoundError(
                "Training dataset manifest "
                f"not found: {manifest_path}"
            )

        raw_manifest = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

        return TrainingDatasetManifest(
            **raw_manifest
        )