import hashlib
import json
from pathlib import Path

import joblib
import pandas as pd
from lightgbm import (
    LGBMRanker,
    log_evaluation,
)
from sklearn.model_selection import (
    train_test_split,
)

from src.domains.matching.evaluation.metrics import (
    RankingMetrics,
)
from src.domains.matching.ml.feature_sets import (
    get_feature_set,
)
from src.domains.matching.ml.ranking_training_result import (
    RankingModelTrainingResult,
)
from src.domains.matching.ml.training_dataset_manifest import (
    TrainingDatasetManifest,
)


class LightGBMRankerTrainer:
    GROUP_COLUMN = "resume_id"
    JOB_ID_COLUMN = "job_id"

    def __init__(
        self,
    ) -> None:
        self.metrics = RankingMetrics()

    def train(
        self,
        *,
        dataset_path: str,
        manifest_path: str,
        model_output_path: str,
        report_output_path: str,
        model_name: str = "lightgbm-lambdarank",
        model_version: str = "v1",
        validation_size: float = 0.25,
        random_state: int = 42,
    ) -> RankingModelTrainingResult:
        manifest = self._load_manifest(
            manifest_path,
        )

        self._validate_dataset_hash(
            dataset_path=dataset_path,
            expected_sha256=(
                manifest.dataset_sha256
            ),
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

        required_columns = {
            self.GROUP_COLUMN,
            self.JOB_ID_COLUMN,
            *feature_set.feature_columns,
            feature_set.label_column,
        }

        missing_columns = (
            required_columns
            - set(dataframe.columns)
        )

        if missing_columns:
            raise ValueError(
                "Training dataset is missing "
                "required columns: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        dataframe = dataframe.copy()

        dataframe[
            self.GROUP_COLUMN
        ] = dataframe[
            self.GROUP_COLUMN
        ].astype(int)

        dataframe[
            self.JOB_ID_COLUMN
        ] = dataframe[
            self.JOB_ID_COLUMN
        ].astype(int)

        dataframe[
            feature_set.label_column
        ] = dataframe[
            feature_set.label_column
        ].astype(int)

        group_ids = sorted(
            dataframe[
                self.GROUP_COLUMN
            ].unique().tolist()
        )

        group_count = len(group_ids)

        if group_count < 2:
            raise ValueError(
                "At least 2 resume groups are "
                "required for ranking training"
            )

        train_group_ids, validation_group_ids = (
            train_test_split(
                group_ids,
                test_size=validation_size,
                random_state=random_state,
            )
        )

        train_dataframe = (
            dataframe[
                dataframe[
                    self.GROUP_COLUMN
                ].isin(
                    train_group_ids
                )
            ]
            .sort_values(
                [
                    self.GROUP_COLUMN,
                    self.JOB_ID_COLUMN,
                ]
            )
            .reset_index(
                drop=True,
            )
        )

        validation_dataframe = (
            dataframe[
                dataframe[
                    self.GROUP_COLUMN
                ].isin(
                    validation_group_ids
                )
            ]
            .sort_values(
                [
                    self.GROUP_COLUMN,
                    self.JOB_ID_COLUMN,
                ]
            )
            .reset_index(
                drop=True,
            )
        )

        if train_dataframe.empty:
            raise ValueError(
                "Training split is empty"
            )

        if validation_dataframe.empty:
            raise ValueError(
                "Validation split is empty"
            )

        feature_columns = list(
            feature_set.feature_columns
        )

        x_train = train_dataframe[
            feature_columns
        ].astype(float)

        y_train = train_dataframe[
            feature_set.label_column
        ].astype(int)

        x_validation = validation_dataframe[
            feature_columns
        ].astype(float)

        y_validation = validation_dataframe[
            feature_set.label_column
        ].astype(int)

        train_group_sizes = (
            self._build_group_sizes(
                train_dataframe
            )
        )

        validation_group_sizes = (
            self._build_group_sizes(
                validation_dataframe
            )
        )

        model = LGBMRanker(
            objective="lambdarank",
            metric="ndcg",
            label_gain=[
                0,
                1,
                3,
                7,
            ],
            n_estimators=150,
            learning_rate=0.05,
            num_leaves=15,
            max_depth=5,
            min_child_samples=2,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_alpha=0.1,
            reg_lambda=0.1,
            random_state=random_state,
            n_jobs=-1,
            verbosity=-1,
        )

        model.fit(
            x_train,
            y_train,
            group=train_group_sizes,
            eval_set=[
                (
                    x_validation,
                    y_validation,
                )
            ],
            eval_group=[
                validation_group_sizes
            ],
            eval_at=[
                5,
            ],
            callbacks=[
                log_evaluation(
                    period=0,
                )
            ],
        )

        validation_predictions = (
            model.predict(
                x_validation
            )
        )

        validation_dataframe = (
            validation_dataframe.copy()
        )

        validation_dataframe[
            "ltr_prediction"
        ] = validation_predictions

        ndcg_at_5, mean_reciprocal_rank = (
            self._evaluate_validation(
                dataframe=(
                    validation_dataframe
                ),
                label_column=(
                    feature_set.label_column
                ),
            )
        )

        feature_importance = {
            feature_name: int(
                importance
            )
            for feature_name, importance
            in zip(
                feature_columns,
                model.feature_importances_,
                strict=True,
            )
        }

        sorted_feature_importance = dict(
            sorted(
                feature_importance.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

        model_path = Path(
            model_output_path,
        )

        model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        pipeline_test_only = (
            len(dataframe) < 500
            or group_count < 50
        )

        artifact = {
            "model": model,
            "model_name": model_name,
            "model_version": model_version,
            "feature_set_identifier": (
                feature_set_identifier
            ),
            "feature_columns": (
                feature_columns
            ),
            "label_column": (
                feature_set.label_column
            ),
            "group_column": (
                self.GROUP_COLUMN
            ),
            "dataset_sha256": (
                manifest.dataset_sha256
            ),
            "label_gain": [
                0,
                1,
                3,
                7,
            ],
            "feature_importance": (
                sorted_feature_importance
            ),
            "pipeline_test_only": (
                pipeline_test_only
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
            "feature_columns": (
                feature_columns
            ),
            "row_count": len(
                dataframe
            ),
            "group_count": group_count,
            "train_row_count": len(
                train_dataframe
            ),
            "validation_row_count": len(
                validation_dataframe
            ),
            "train_group_count": len(
                train_group_ids
            ),
            "validation_group_count": len(
                validation_group_ids
            ),
            "train_group_ids": sorted(
                int(group_id)
                for group_id
                in train_group_ids
            ),
            "validation_group_ids": sorted(
                int(group_id)
                for group_id
                in validation_group_ids
            ),
            "train_group_sizes": (
                train_group_sizes
            ),
            "validation_group_sizes": (
                validation_group_sizes
            ),
            "metrics": {
                "ndcg_at_5": (
                    ndcg_at_5
                ),
                "mean_reciprocal_rank": (
                    mean_reciprocal_rank
                ),
            },
            "feature_importance": (
                sorted_feature_importance
            ),
            "pipeline_test_only": (
                pipeline_test_only
            ),
            "warning": (
                "This model is intended only "
                "for pipeline testing with the "
                "current small dataset."
                if pipeline_test_only
                else None
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

        return RankingModelTrainingResult(
            model_name=model_name,
            model_version=model_version,
            dataset_path=dataset_path,
            manifest_path=manifest_path,
            feature_set_identifier=(
                feature_set_identifier
            ),
            row_count=len(
                dataframe
            ),
            group_count=group_count,
            train_row_count=len(
                train_dataframe
            ),
            validation_row_count=len(
                validation_dataframe
            ),
            train_group_count=len(
                train_group_ids
            ),
            validation_group_count=len(
                validation_group_ids
            ),
            ndcg_at_5=ndcg_at_5,
            mean_reciprocal_rank=(
                mean_reciprocal_rank
            ),
            model_path=str(
                model_path
            ),
            report_path=str(
                report_path
            ),
            pipeline_test_only=(
                pipeline_test_only
            ),
        )

    def _build_group_sizes(
        self,
        dataframe: pd.DataFrame,
    ) -> list[int]:
        return [
            int(group_size)
            for group_size
            in dataframe.groupby(
                self.GROUP_COLUMN,
                sort=True,
            ).size().tolist()
        ]

    def _evaluate_validation(
        self,
        *,
        dataframe: pd.DataFrame,
        label_column: str,
    ) -> tuple[float, float]:
        ndcg_values: list[float] = []
        reciprocal_rank_values: list[
            float
        ] = []

        for _, group in dataframe.groupby(
            self.GROUP_COLUMN,
            sort=True,
        ):
            ranked_group = group.sort_values(
                "ltr_prediction",
                ascending=False,
            )

            predicted_job_ids = [
                int(job_id)
                for job_id
                in ranked_group[
                    self.JOB_ID_COLUMN
                ].tolist()
            ]

            relevance_grades = {
                int(row[self.JOB_ID_COLUMN]):
                    int(row[label_column])
                for _, row
                in group.iterrows()
            }

            relevant_job_ids = {
                job_id
                for job_id, grade
                in relevance_grades.items()
                if grade > 0
            }

            ndcg_values.append(
                self.metrics.ndcg_at_k(
                    predicted_job_ids=(
                        predicted_job_ids
                    ),
                    relevance_grades=(
                        relevance_grades
                    ),
                    k=5,
                )
            )

            reciprocal_rank_values.append(
                self.metrics.reciprocal_rank(
                    predicted_job_ids=(
                        predicted_job_ids
                    ),
                    relevant_job_ids=(
                        relevant_job_ids
                    ),
                )
            )

        return (
            self._mean(
                ndcg_values
            ),
            self._mean(
                reciprocal_rank_values
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

    def _validate_dataset_hash(
        self,
        *,
        dataset_path: str,
        expected_sha256: str,
    ) -> None:
        path = Path(
            dataset_path,
        )

        if not path.exists():
            raise FileNotFoundError(
                "Training dataset not found: "
                f"{dataset_path}"
            )

        digest = hashlib.sha256()

        with path.open(
            "rb",
        ) as input_file:
            while chunk := input_file.read(
                1024 * 1024
            ):
                digest.update(
                    chunk
                )

        actual_sha256 = (
            digest.hexdigest()
        )

        if actual_sha256 != expected_sha256:
            raise ValueError(
                "Training dataset SHA-256 does "
                "not match its manifest"
            )

    def _mean(
        self,
        values: list[float],
    ) -> float | None:
        if not values:
            return None

        return float(
            sum(values) / len(values)
        )