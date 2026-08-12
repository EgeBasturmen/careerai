import argparse
import json
from pathlib import Path

from src.core.database.session import (
    SessionLocal,
)
from src.domains.knowledge.evaluation.dataset_evaluator import (
    DatasetEvaluator,
)
from src.domains.knowledge.evaluation.evaluation_dataset_loader import (
    EvaluationDatasetLoader,
)
from src.domains.knowledge.evaluation.retrieval_evaluator import (
    RetrievalEvaluator,
)
from src.domains.knowledge.services.knowledge_retriever import (
    KnowledgeRetriever,
)


DEFAULT_DATASET_PATH = Path(
    "datasets/knowledge/evaluation/"
    "careerai_rag_v1.json"
)

DEFAULT_K = 5
DEFAULT_MINIMUM_SIMILARITY = 0.0


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate CareerAI knowledge retrieval "
            "against a versioned dataset."
        ),
    )

    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help=(
            "Path to the retrieval evaluation "
            "dataset JSON file."
        ),
    )

    parser.add_argument(
        "--k",
        type=int,
        default=DEFAULT_K,
        help=(
            "Maximum number of retrieved documents "
            "used for metric calculation."
        ),
    )

    parser.add_argument(
        "--minimum-similarity",
        type=float,
        default=DEFAULT_MINIMUM_SIMILARITY,
        help=(
            "Minimum retrieval similarity threshold."
        ),
    )

    parser.add_argument(
        "--output-path",
        type=Path,
        default=None,
        help=(
            "Optional JSON path where the evaluation "
            "report will be written."
        ),
    )

    return parser.parse_args()


def validate_arguments(
    arguments: argparse.Namespace,
) -> None:
    if arguments.k <= 0:
        raise ValueError(
            "--k must be greater than zero"
        )

    if not 0.0 <= arguments.minimum_similarity <= 1.0:
        raise ValueError(
            "--minimum-similarity must be "
            "between 0.0 and 1.0"
        )


def print_report(
    report,
    *,
    k: int,
    minimum_similarity: float,
) -> None:
    print()
    print("=" * 60)
    print("CareerAI Knowledge Retrieval Evaluation")
    print("=" * 60)

    print(
        f"Dataset              : "
        f"{report.dataset_name}"
    )

    print(
        f"Version              : "
        f"{report.version}"
    )

    print(
        f"Case count           : "
        f"{report.case_count}"
    )

    print(
        f"K                    : "
        f"{k}"
    )

    print(
        f"Minimum similarity   : "
        f"{minimum_similarity:.4f}"
    )

    print("-" * 60)

    print(
        f"Mean Precision@{k:<3} : "
        f"{report.mean_precision_at_k:.4f}"
    )

    print(
        f"Mean Recall@{k:<6} : "
        f"{report.mean_recall_at_k:.4f}"
    )

    print(
        f"Mean MRR             : "
        f"{report.mean_mrr:.4f}"
    )

    print(
        f"Mean NDCG@{k:<8} : "
        f"{report.mean_ndcg_at_k:.4f}"
    )

    print("=" * 60)
    print()


def save_report(
    *,
    output_path: Path,
    report,
    dataset_path: Path,
    k: int,
    minimum_similarity: float,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "dataset_path": str(
            dataset_path
        ),
        "dataset_name": (
            report.dataset_name
        ),
        "version": report.version,
        "case_count": (
            report.case_count
        ),
        "configuration": {
            "k": k,
            "minimum_similarity": (
                minimum_similarity
            ),
        },
        "metrics": {
            "mean_precision_at_k": (
                report.mean_precision_at_k
            ),
            "mean_recall_at_k": (
                report.mean_recall_at_k
            ),
            "mean_mrr": (
                report.mean_mrr
            ),
            "mean_ndcg_at_k": (
                report.mean_ndcg_at_k
            ),
        },
    }

    output_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Evaluation report saved to: "
        f"{output_path}"
    )


def main() -> None:
    arguments = parse_arguments()

    validate_arguments(
        arguments
    )

    dataset_loader = (
        EvaluationDatasetLoader()
    )

    dataset = dataset_loader.load(
        arguments.dataset_path
    )

    db = SessionLocal()

    try:
        retriever = KnowledgeRetriever(
            db,
        )

        evaluator = DatasetEvaluator(
            retriever=retriever,
            retrieval_evaluator=(
                RetrievalEvaluator()
            ),
        )

        report = evaluator.evaluate(
            dataset=dataset,
            k=arguments.k,
            minimum_similarity=(
                arguments.minimum_similarity
            ),
        )

        print_report(
            report,
            k=arguments.k,
            minimum_similarity=(
                arguments.minimum_similarity
            ),
        )

        if arguments.output_path:
            save_report(
                output_path=(
                    arguments.output_path
                ),
                report=report,
                dataset_path=(
                    arguments.dataset_path
                ),
                k=arguments.k,
                minimum_similarity=(
                    arguments.minimum_similarity
                ),
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()