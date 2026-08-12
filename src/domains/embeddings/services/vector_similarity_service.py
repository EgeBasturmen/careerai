import math


class VectorSimilarityService:
    def cosine_similarity(
        self,
        first_vector: list[float],
        second_vector: list[float],
    ) -> float:
        if len(first_vector) != len(second_vector):
            raise ValueError(
                "Vectors must have the same dimension"
            )

        if not first_vector:
            raise ValueError(
                "Vectors cannot be empty"
            )

        dot_product = sum(
            first_value * second_value
            for first_value, second_value in zip(
                first_vector,
                second_vector,
                strict=True,
            )
        )

        first_norm = math.sqrt(
            sum(
                value * value
                for value in first_vector
            )
        )

        second_norm = math.sqrt(
            sum(
                value * value
                for value in second_vector
            )
        )

        if first_norm == 0 or second_norm == 0:
            raise ValueError(
                "Cannot calculate similarity "
                "for a zero vector"
            )

        return dot_product / (
            first_norm * second_norm
        )