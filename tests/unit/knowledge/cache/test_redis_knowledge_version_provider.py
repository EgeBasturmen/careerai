from unittest.mock import Mock

from redis.exceptions import RedisError

from src.domains.knowledge.cache.redis_knowledge_version_provider import (
    RedisKnowledgeVersionProvider,
)


def test_provider_name_is_redis(
) -> None:
    redis_client = Mock()

    provider = (
        RedisKnowledgeVersionProvider(
            redis_client=redis_client,
        )
    )

    assert provider.provider_name == "redis"


def test_get_version_returns_existing_version(
) -> None:
    redis_client = Mock()

    redis_client.get.return_value = b"7"

    provider = (
        RedisKnowledgeVersionProvider(
            redis_client=redis_client,
        )
    )

    result = provider.get_version()

    assert result == 7

    redis_client.get.assert_called_once_with(
        provider.KEY
    )


def test_get_version_initializes_missing_version(
) -> None:
    redis_client = Mock()

    redis_client.get.return_value = None
    redis_client.set.return_value = True

    provider = (
        RedisKnowledgeVersionProvider(
            redis_client=redis_client,
        )
    )

    result = provider.get_version()

    assert result == 1

    redis_client.set.assert_called_once_with(
        name=provider.KEY,
        value=provider.DEFAULT_VERSION,
        nx=True,
    )


def test_get_version_returns_existing_version_when_another_process_initialized_it(
) -> None:
    redis_client = Mock()

    redis_client.get.side_effect = [
        None,
        b"4",
    ]

    redis_client.set.return_value = None

    provider = (
        RedisKnowledgeVersionProvider(
            redis_client=redis_client,
        )
    )

    result = provider.get_version()

    assert result == 4

    redis_client.set.assert_called_once_with(
        name=provider.KEY,
        value=provider.DEFAULT_VERSION,
        nx=True,
    )


def test_get_version_resets_invalid_value(
) -> None:
    redis_client = Mock()

    redis_client.get.return_value = (
        b"invalid"
    )

    provider = (
        RedisKnowledgeVersionProvider(
            redis_client=redis_client,
        )
    )

    result = provider.get_version()

    assert result == 1

    redis_client.set.assert_called_once_with(
        name=provider.KEY,
        value=provider.DEFAULT_VERSION,
    )


def test_get_version_resets_value_below_default(
) -> None:
    redis_client = Mock()

    redis_client.get.return_value = b"0"

    provider = (
        RedisKnowledgeVersionProvider(
            redis_client=redis_client,
        )
    )

    result = provider.get_version()

    assert result == 1

    redis_client.set.assert_called_once_with(
        name=provider.KEY,
        value=provider.DEFAULT_VERSION,
    )


def test_get_version_returns_default_when_redis_fails(
) -> None:
    redis_client = Mock()

    redis_client.get.side_effect = (
        RedisError()
    )

    provider = (
        RedisKnowledgeVersionProvider(
            redis_client=redis_client,
        )
    )

    result = provider.get_version()

    assert result == 1


def test_increment_version_returns_incremented_value(
) -> None:
    redis_client = Mock()

    redis_client.incr.return_value = 6

    provider = (
        RedisKnowledgeVersionProvider(
            redis_client=redis_client,
        )
    )

    result = provider.increment_version()

    assert result == 6

    redis_client.incr.assert_called_once_with(
        provider.KEY
    )


def test_increment_version_returns_default_when_redis_fails(
) -> None:
    redis_client = Mock()

    redis_client.incr.side_effect = (
        RedisError()
    )

    provider = (
        RedisKnowledgeVersionProvider(
            redis_client=redis_client,
        )
    )

    result = provider.increment_version()

    assert result == 1