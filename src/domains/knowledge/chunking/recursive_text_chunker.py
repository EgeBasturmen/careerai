from src.domains.knowledge.chunking.text_chunk import (
    TextChunk,
)


class RecursiveTextChunker:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ):
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero"
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative"
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller "
                "than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(
        self,
        text: str,
    ) -> list[TextChunk]:
        normalized_text = self._normalize_text(
            text,
        )

        if not normalized_text:
            return []

        chunks: list[TextChunk] = []

        start = 0
        chunk_index = 0
        text_length = len(
            normalized_text
        )

        while start < text_length:
            ideal_end = min(
                start + self.chunk_size,
                text_length,
            )

            end = self._find_chunk_end(
                text=normalized_text,
                start=start,
                ideal_end=ideal_end,
            )

            content = normalized_text[
                start:end
            ].strip()

            if content:
                chunks.append(
                    TextChunk(
                        index=chunk_index,
                        content=content,
                        character_count=len(
                            content
                        ),
                        start_character=start,
                        end_character=end,
                    )
                )

                chunk_index += 1

            if end >= text_length:
                break

            next_start = (
                end - self.chunk_overlap
            )

            if next_start <= start:
                next_start = end

            start = next_start

        return chunks

    def _find_chunk_end(
        self,
        text: str,
        start: int,
        ideal_end: int,
    ) -> int:
        if ideal_end >= len(text):
            return len(text)

        separators = (
            "\n\n",
            "\n",
            ". ",
            " ",
        )

        minimum_end = start + (
            self.chunk_size // 2
        )

        for separator in separators:
            separator_position = text.rfind(
                separator,
                minimum_end,
                ideal_end,
            )

            if separator_position != -1:
                return (
                    separator_position
                    + len(separator)
                )

        return ideal_end

    def _normalize_text(
        self,
        text: str,
    ) -> str:
        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        normalized_lines: list[str] = []
        previous_blank = False

        for line in lines:
            is_blank = not line

            if is_blank and previous_blank:
                continue

            normalized_lines.append(
                line
            )

            previous_blank = is_blank

        return "\n".join(
            normalized_lines
        ).strip()