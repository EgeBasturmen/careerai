import pytest

from src.domains.knowledge.cache.memory_knowledge_version_provider import (
    MemoryKnowledgeVersionProvider,
)


def test_provider_returns_default_version(
) -> None:
    provider = (
        MemoryKnowledgeVersionProvider()
    )

    result = provider.get_version()

    assert result == 1


def test_provider_returns_configured_initial_version(
) -> None:
    provider = (
        MemoryKnowledgeVersionProvider(
            initial_version=5,
        )
    )

    result = provider.get_version()

    assert result == 5


def test_increment_version_returns_new_version(
) -> None:
    provider = (
        MemoryKnowledgeVersionProvider(
            initial_version=3,
        )
    )

    result = (
        provider.increment_version()
    )

    assert result == 4
    assert provider.get_version() == 4


def test_increment_version_can_be_called_multiple_times(
) -> None:
    provider = (
        MemoryKnowledgeVersionProvider()
    )

    first_result = (
        provider.increment_version()
    )

    second_result = (
        provider.increment_version()
    )

    assert first_result == 2
    assert second_result == 3
    assert provider.get_version() == 3


def test_provider_name_is_memory(
) -> None:
    provider = (
        MemoryKnowledgeVersionProvider()
    )

    assert provider.provider_name == "memory"


@pytest.mark.parametrize(
    "initial_version",
    [
        0,
        -1,
        -100,
    ],
)
def test_provider_rejects_invalid_initial_version(
    initial_version: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "initial_version must be "
            "greater than or equal to 1"
        ),
    ):
        MemoryKnowledgeVersionProvider(
            initial_version=initial_version,
        )