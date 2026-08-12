import json

from src.domains.knowledge.evaluation.evaluation_dataset_loader import (
    EvaluationDatasetLoader,
)


def test_load_dataset(
    tmp_path,
):
    dataset = {
        "dataset_name": "careerai-rag",
        "version": "v1",
        "cases": [
            {
                "case_id": "1",
                "query": "python",
                "expected_document_ids": [1],
            }
        ],
    }

    path = tmp_path / "dataset.json"

    path.write_text(
        json.dumps(dataset),
        encoding="utf-8",
    )

    loader = (
        EvaluationDatasetLoader()
    )

    loaded = loader.load(path)

    assert (
        loaded.dataset_name
        == "careerai-rag"
    )

    assert loaded.version == "v1"

    assert len(loaded.cases) == 1

    assert (
        loaded.cases[0].query
        == "python"
    )