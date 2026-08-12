from src.domains.knowledge.schemas.query_rewrite_schema import (
    QueryRewriteRequest,
)
from src.domains.knowledge.services.query_rewriter import (
    QueryRewriter,
)


def main() -> None:
    rewriter = QueryRewriter()

    response = rewriter.rewrite(
        QueryRewriteRequest(
            query=(
                "how ım gonna python developer"
            ),
            category="career",
            language="en",
        )
    )

    print(
        response.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()