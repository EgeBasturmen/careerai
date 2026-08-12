from src.domains.embeddings.clients.factory import (
    get_embedding_client,
)
from src.domains.embeddings.services.embedding_service import (
    EmbeddingService,
)
from src.domains.embeddings.services.vector_similarity_service import (
    VectorSimilarityService,
)


def main() -> None:
    client = get_embedding_client()

    embedding_service = EmbeddingService(
        client=client,
    )

    similarity_service = (
        VectorSimilarityService()
    )

    resume_text = (
        "Junior backend developer with Python, "
        "FastAPI, PostgreSQL, Docker and Redis "
        "experience."
    )

    relevant_job_text = (
        "Python API engineer required for building "
        "backend services with containers, SQL "
        "databases and caching systems."
    )

    unrelated_job_text = (
        "Human resources intern responsible for "
        "recruitment, employee communication and "
        "performance management."
    )

    result = embedding_service.embed_texts(
        [
            resume_text,
            relevant_job_text,
            unrelated_job_text,
        ]
    )

    resume_vector = result.vectors[0]
    relevant_job_vector = result.vectors[1]
    unrelated_job_vector = result.vectors[2]

    relevant_similarity = (
        similarity_service.cosine_similarity(
            resume_vector,
            relevant_job_vector,
        )
    )

    unrelated_similarity = (
        similarity_service.cosine_similarity(
            resume_vector,
            unrelated_job_vector,
        )
    )

    print(
        "Provider:",
        result.provider,
    )

    print(
        "Model:",
        result.model,
    )

    print(
        "Dimension:",
        result.dimension,
    )

    print(
        "Relevant similarity:",
        round(relevant_similarity, 4),
    )

    print(
        "Unrelated similarity:",
        round(unrelated_similarity, 4),
    )

    assert (
        relevant_similarity
        > unrelated_similarity
    )

    print(
        "Semantic similarity test passed."
    )


if __name__ == "__main__":
    main()