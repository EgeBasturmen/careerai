import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.domains.matching.ml.feature_sets import (
    MatchFeatureSet,
)


@dataclass(slots=True)
class TrainingDatasetManifest:
    dataset_name: str
    dataset_version: str

    dataset_path: str
    dataset_format: str
    dataset_sha256: str

    generated_at: str

    feature_set_name: str
    feature_set_version: str
    feature_columns: list[str]
    label_column: str

    algorithm_version: str | None

    row_count: int
    label_distribution: dict[str, int]

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return asdict(self)


class TrainingDatasetManifestBuilder:
    def build(
        self,
        dataset_name: str,
        dataset_version: str,
        dataset_path: str,
        dataset_format: str,
        feature_set: MatchFeatureSet,
        algorithm_version: str | None,
        row_count: int,
        label_distribution: dict[str, int],
    ) -> TrainingDatasetManifest:
        path = Path(
            dataset_path,
        )

        if not path.exists():
            raise FileNotFoundError(
                "Training dataset not found: "
                f"{dataset_path}"
            )

        return TrainingDatasetManifest(
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            dataset_path=dataset_path,
            dataset_format=dataset_format,
            dataset_sha256=(
                self._calculate_sha256(
                    path,
                )
            ),
            generated_at=datetime.now(
                timezone.utc,
            ).isoformat(),
            feature_set_name=(
                feature_set.name
            ),
            feature_set_version=(
                feature_set.version
            ),
            feature_columns=list(
                feature_set.feature_columns
            ),
            label_column=(
                feature_set.label_column
            ),
            algorithm_version=(
                algorithm_version
            ),
            row_count=row_count,
            label_distribution=(
                label_distribution
            ),
        )

    def save(
        self,
        manifest: TrainingDatasetManifest,
        manifest_path: str,
    ) -> None:
        path = Path(
            manifest_path,
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                manifest.to_dict(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def _calculate_sha256(
        self,
        path: Path,
    ) -> str:
        digest = hashlib.sha256()

        with path.open(
            "rb",
        ) as input_file:
            while chunk := input_file.read(
                1024 * 1024
            ):
                digest.update(
                    chunk,
                )

        return digest.hexdigest()