# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF IndexingService.
#
# Responsibilities:
# - Validate logical index-provider resolution.
# - Validate supported representation indexing.
# - Validate idempotent indexing delegation.
# - Validate representation deletion delegation.
# - Validate unsupported representation rejection.
# - Validate invalid registry and provider behavior.
#
# Must Not:
# - Test physical vector databases or search engines.
# - Test representation generation.
# - Test retrieval, reranking, evidence, or context construction.
# - Test index lifecycle, promotion, or rollback.
# - Test concurrency, batching, or NFT execution policy.
# - Depend on external RAG or orchestration frameworks.

import pytest

from alhf.rag.indexing.indexing_service import IndexingService
from alhf.rag.indexing.interfaces.index_registry import IndexRegistry
from alhf.rag.indexing.providers.in_memory_index_provider import (
    InMemoryIndexProvider,
)
from alhf.rag.indexing.providers.in_memory_index_registry import (
    InMemoryIndexRegistry,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)


def _representation(
    *,
    kind: RepresentationKind = RepresentationKind.LEXICAL,
) -> KnowledgeRepresentation:
    return KnowledgeRepresentation(
        representation_id="representation-001",
        knowledge_unit_ref="unit-001",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
        kind=kind,
        payload=b"enterprise knowledge",
        media_type="text/plain",
        strategy_ref="deterministic-text-representation",
        strategy_version="1.0",
    )


def _provider() -> InMemoryIndexProvider:
    return InMemoryIndexProvider()


def _service(
    provider: InMemoryIndexProvider | None = None,
) -> tuple[IndexingService, InMemoryIndexProvider]:
    provider = provider or _provider()
    registry = InMemoryIndexRegistry()

    registry.register(
        index_ref="knowledge-index",
        provider=provider,
    )

    return (
        IndexingService(
            registry=registry,
        ),
        provider,
    )


def test_create_indexing_service() -> None:
    service, _ = _service()

    assert isinstance(
        service,
        IndexingService,
    )


def test_index_delegates_to_resolved_provider() -> None:
    service, provider = _service()
    representation = _representation()

    service.index(
        index_ref="knowledge-index",
        representation=representation,
    )

    assert provider.get(
        representation.representation_id
    ) is representation


def test_index_is_idempotent() -> None:
    service, provider = _service()
    representation = _representation()

    service.index(
        index_ref="knowledge-index",
        representation=representation,
    )
    service.index(
        index_ref="knowledge-index",
        representation=representation,
    )

    assert len(provider) == 1


def test_index_reference_is_normalized() -> None:
    service, provider = _service()
    representation = _representation()

    service.index(
        index_ref="  knowledge-index  ",
        representation=representation,
    )

    assert representation.representation_id in provider


def test_delete_delegates_to_resolved_provider() -> None:
    service, provider = _service()
    representation = _representation()

    service.index(
        index_ref="knowledge-index",
        representation=representation,
    )
    service.delete(
        index_ref="knowledge-index",
        representation_id=representation.representation_id,
    )

    assert representation.representation_id not in provider


def test_delete_missing_representation_is_idempotent() -> None:
    service, provider = _service()

    service.delete(
        index_ref="knowledge-index",
        representation_id="missing-representation",
    )

    assert len(provider) == 0


def test_invalid_registry_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="registry must be an instance of IndexRegistry",
    ):
        IndexingService(
            registry="invalid-registry"
        )


def test_invalid_representation_is_rejected() -> None:
    service, _ = _service()

    with pytest.raises(
        TypeError,
        match=(
            "representation must be an instance of "
            "KnowledgeRepresentation"
        ),
    ):
        service.index(
            index_ref="knowledge-index",
            representation="invalid-representation",
        )


def test_unsupported_representation_is_rejected() -> None:
    service, _ = _service()

    with pytest.raises(
        ValueError,
        match=(
            "resolved index provider does not support "
            "KnowledgeRepresentation"
        ),
    ):
        service.index(
            index_ref="knowledge-index",
            representation=_representation(
                kind=RepresentationKind.DENSE,
            ),
        )


def test_unknown_index_is_rejected() -> None:
    service, _ = _service()

    with pytest.raises(
        LookupError,
        match="index provider not found: missing-index",
    ):
        service.index(
            index_ref="missing-index",
            representation=_representation(),
        )


@pytest.mark.parametrize(
    "index_ref",
    ("", "   "),
)
def test_empty_index_reference_is_rejected(
    index_ref: str,
) -> None:
    service, _ = _service()

    with pytest.raises(
        ValueError,
        match="index_ref cannot be empty",
    ):
        service.index(
            index_ref=index_ref,
            representation=_representation(),
        )


def test_invalid_index_reference_is_rejected() -> None:
    service, _ = _service()

    with pytest.raises(
        TypeError,
        match="index_ref must be a string",
    ):
        service.index(
            index_ref=123,
            representation=_representation(),
        )


@pytest.mark.parametrize(
    "representation_id",
    ("", "   "),
)
def test_empty_delete_representation_id_is_rejected(
    representation_id: str,
) -> None:
    service, _ = _service()

    with pytest.raises(
        ValueError,
        match="representation_id cannot be empty",
    ):
        service.delete(
            index_ref="knowledge-index",
            representation_id=representation_id,
        )


class InvalidProviderRegistry(IndexRegistry):
    """Registry intentionally returning an invalid provider."""

    def resolve(
        self,
        index_ref: str,
    ) -> object:
        return "invalid-provider"

    def contains(
        self,
        index_ref: str,
    ) -> bool:
        return True


def test_invalid_registry_provider_is_rejected() -> None:
    service = IndexingService(
        registry=InvalidProviderRegistry()
    )

    with pytest.raises(
        TypeError,
        match="registry must return IndexProvider",
    ):
        service.index(
            index_ref="knowledge-index",
            representation=_representation(),
        )
