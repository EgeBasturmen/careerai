class QueryRewritePromptBuilder:
    PROMPT_NAME = "knowledge-query-rewrite"
    PROMPT_VERSION = "v1"

    def build(
        self,
        *,
        query: str,
        category: str | None,
        language: str | None,
    ) -> str:
        category_value = (
            category
            if category is not None
            else "not specified"
        )

        language_value = (
            language
            if language is not None
            else "not specified"
        )

        return (
            "You are a search query rewriting system.\n\n"
            "Your task is to rewrite the user's query so that "
            "a knowledge retrieval system can find more relevant "
            "documents.\n\n"
            "Rules:\n"
            "1. Preserve the original meaning.\n"
            "2. Correct spelling and grammar errors.\n"
            "3. Expand unclear or incomplete wording.\n"
            "4. Do not answer the question.\n"
            "5. Do not add unrelated assumptions.\n"
            "6. Return only valid JSON.\n"
            "7. Keep the rewritten query concise.\n"
            "8. Use the requested language when specified.\n\n"
            "Required JSON format:\n"
            "{\n"
            '  "rewritten_query": "string"\n'
            "}\n\n"
            f"Category: {category_value}\n"
            f"Language: {language_value}\n"
            f"Original query: {query}"
        )