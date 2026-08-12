import json
from typing import Any


class QueryRewriteResponseParser:
    MAXIMUM_QUERY_LENGTH = 4000

    def parse(
        self,
        raw_response: str,
    ) -> str:
        cleaned_response = (
            self._clean_response(
                raw_response
            )
        )

        try:
            payload: Any = json.loads(
                cleaned_response
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Query rewrite response is not "
                "valid JSON"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "Query rewrite response must "
                "be a JSON object"
            )

        rewritten_query = payload.get(
            "rewritten_query"
        )

        if not isinstance(
            rewritten_query,
            str,
        ):
            raise ValueError(
                "rewritten_query must be "
                "a string"
            )

        normalized_query = " ".join(
            rewritten_query
            .strip()
            .split()
        )

        if not normalized_query:
            raise ValueError(
                "rewritten_query cannot "
                "be empty"
            )

        if (
            len(normalized_query)
            > self.MAXIMUM_QUERY_LENGTH
        ):
            raise ValueError(
                "rewritten_query exceeds "
                "maximum length"
            )

        return normalized_query

    def _clean_response(
        self,
        raw_response: str,
    ) -> str:
        cleaned_response = (
            raw_response.strip()
        )

        if cleaned_response.startswith(
            "```json"
        ):
            cleaned_response = (
                cleaned_response[
                    len("```json"):
                ]
            )

        elif cleaned_response.startswith(
            "```"
        ):
            cleaned_response = (
                cleaned_response[
                    len("```"):
                ]
            )

        if cleaned_response.endswith(
            "```"
        ):
            cleaned_response = (
                cleaned_response[:-3]
            )

        return cleaned_response.strip()