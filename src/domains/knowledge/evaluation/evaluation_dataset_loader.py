import json
from pathlib import Path

from src.domains.knowledge.evaluation.evaluation_dataset import (
    EvaluationDataset,
)


class EvaluationDatasetLoader:
    def load(
        self,
        dataset_path: str | Path,
    ) -> EvaluationDataset:
        path = Path(dataset_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            payload = json.load(file)

        return EvaluationDataset.model_validate(
            payload
        )