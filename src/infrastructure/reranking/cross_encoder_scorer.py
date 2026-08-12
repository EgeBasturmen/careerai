from collections.abc import Sequence

import torch
from sentence_transformers import CrossEncoder


class CrossEncoderScorer:
    def __init__(
        self,
        *,
        model_name: str,
        batch_size: int = 16,
    ) -> None:
        normalized_model_name = (
            model_name.strip()
        )

        if not normalized_model_name:
            raise ValueError(
                "CrossEncoder model name "
                "cannot be empty"
            )

        if batch_size < 1:
            raise ValueError(
                "CrossEncoder batch size "
                "must be positive"
            )

        self.model_name = (
            normalized_model_name
        )
        self.batch_size = batch_size

        self.model = CrossEncoder(
            self.model_name,
            activation_fn=(
                torch.nn.Sigmoid()
            ),
        )

    def score(
        self,
        *,
        query_text: str,
        passages: Sequence[str],
    ) -> list[float]:
        normalized_query = (
            query_text.strip()
        )

        if not normalized_query:
            raise ValueError(
                "CrossEncoder query "
                "cannot be empty"
            )

        if not passages:
            return []

        normalized_passages = [
            passage.strip()
            for passage in passages
        ]

        if any(
            not passage
            for passage in normalized_passages
        ):
            raise ValueError(
                "CrossEncoder passages "
                "cannot be empty"
            )

        pairs = [
            (
                normalized_query,
                passage,
            )
            for passage in (
                normalized_passages
            )
        ]

        predicted_scores = (
            self.model.predict(
                pairs,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
        )

        return [
            float(score)
            for score in predicted_scores
        ]