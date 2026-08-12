from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TextChunk:
    index: int
    content: str
    character_count: int

    start_character: int
    end_character: int