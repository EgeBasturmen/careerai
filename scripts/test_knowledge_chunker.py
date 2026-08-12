from src.domains.knowledge.chunking.recursive_text_chunker import (
    RecursiveTextChunker,
)


def main() -> None:
    text = """
    FastAPI is a modern Python web framework.
    It supports asynchronous request handling and
    automatic OpenAPI documentation.

    PostgreSQL is a relational database system.
    It can also support vector similarity search
    through the pgvector extension.

    Redis can be used for caching and background
    job coordination. Celery commonly uses Redis
    as a broker or result backend.
    """

    chunker = RecursiveTextChunker(
        chunk_size=160,
        chunk_overlap=30,
    )

    chunks = chunker.split(
        text,
    )

    for chunk in chunks:
        print(
            f"\n--- Chunk {chunk.index} ---"
        )

        print(
            f"Characters: "
            f"{chunk.character_count}"
        )

        print(
            f"Range: "
            f"{chunk.start_character}-"
            f"{chunk.end_character}"
        )

        print(
            chunk.content
        )


if __name__ == "__main__":
    main()