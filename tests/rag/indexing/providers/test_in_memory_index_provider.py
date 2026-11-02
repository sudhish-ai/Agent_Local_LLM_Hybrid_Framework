# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF InMemoryIndexProvider.
#
# Responsibilities:
# - Validate stable provider identity and version.
# - Validate lexical representation compatibility.
# - Validate idempotent representation upsert.
# - Validate representation retrieval and iteration.
# - Validate idempotent deletion.
# - Validate indexed representation identity preservation.
# - Validate invalid and unsupported inputs.
#
# Must Not:
# - Test vector similarity or ranking.
# - Test retrieval, reranking, evidence, or context construction.
# - Test Index Intelligence or lifecycle promotion.
# - Test concurrency, batching, or NFT execution policy.
# - Depend on external RAG or orchestration frameworks.

from collections.abc import Iterator

import pytest

from alhf.rag.indexing.providers.in_memory_index_provider import (
    InMemoryIndexProvider,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)


def _representation(
    *,
    representation_id: str = "representation-001",
    kind: RepresentationKind = RepresentationKind.LEXICAL,
) -> KnowledgeRepresentation:
    return KnowledgeRepresentation(
        representation_id=representation_id,
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


def test_provider_exposes_stable_identity() -> None:
    provider = InMemoryIndexProvider()

    assert provider.provider_ref == "in-memory-index"
    assert provider.provider_version == "1.0"


def test_provider_supports_lexical_representation() -> None:
    provider = InMemoryIndexProvider()

    assert provider.supports(
        _representation()
    ) is True


def test_provider_rejects_dense_representation() -> None:
    provider = InMemoryIndexProvider()

    assert provider.supports(
        _representation(
            kind=RepresentationKind.DENSE,
        )
    ) is False


def test_provider_rejects_invalid_object() -> None:
    provider = InMemoryIndexProvider()

    assert provider.supports(
        "invalid-representation"
    ) is False


def test_new_provider_is_empty() -> None:
    provider = InMemoryIndexProvider()

    assert len(provider) == 0


def test_upsert_indexes_representation() -> None:
    provider = InMemoryIndexProvider()
    representation = _representation()

    provider.upsert(
        representation
    )

    assert len(provider) == 1
    assert representation.representation_id in provider


def test_get_returns_indexed_representation() -> None:
    provider = InMemoryIndexProvider()
    representation = _representation()

    provider.upsert(
        representation
    )

    assert provider.get(
        representation.representation_id
    ) is representation


def test_get_returns_none_for_missing_representation() -> None:
    provider = InMemoryIndexProvider()

    assert provider.get(
        "missing-representation"
    ) is None


def test_repeated_upsert_is_idempotent() -> None:
    provider = InMemoryIndexProvider()
    representation = _representation()

    provider.upsert(
        representation
    )
    provider.upsert(
        representation
    )

    assert len(provider) == 1


def test_upsert_replaces_same_representation_identity() -> None:
    provider = InMemoryIndexProvider()
    first = _representation()
    second = _representation()

    provider.upsert(
        first
    )
    provider.upsert(
        second
    )

    assert len(provider) == 1
    assert provider.get(
        "representation-001"
    ) is second


def test_representations_returns_iterator() -> None:
    provider = InMemoryIndexProvider()

    provider.upsert(
        _representation()
    )

    indexed = provider.representations()

    assert isinstance(
        indexed,
        Iterator,
    )


def test_representations_yields_indexed_values() -> None:
    provider = InMemoryIndexProvider()
    first = _representation(
        representation_id="representation-001",
    )
    second = _representation(
        representation_id="representation-002",
    )

    provider.upsert(first)
    provider.upsert(second)

    assert tuple(
        provider.representations()
    ) == (
        first,
        second,
    )


def test_delete_removes_representation() -> None:
    provider = InMemoryIndexProvider()
    representation = _representation()

    provider.upsert(
        representation
    )
    provider.delete(
        representation.representation_id
    )

    assert len(provider) == 0
    assert representation.representation_id not in provider


def test_delete_missing_representation_is_idempotent() -> None:
    provider = InMemoryIndexProvider()

    provider.delete(
        "missing-representation"
    )

    assert len(provider) == 0


def test_upsert_invalid_representation_is_rejected() -> None:
    provider = InMemoryIndexProvider()

    with pytest.raises(
        TypeError,
        match=(
            "representation must be an instance of "
            "KnowledgeRepresentation"
        ),
    ):
        provider.upsert(
            "invalid-representation"
        )


def test_upsert_unsupported_representation_is_rejected() -> None:
    provider = InMemoryIndexProvider()

    with pytest.raises(
        ValueError,
        match=(
            "InMemoryIndexProvider requires "
            "a lexical KnowledgeRepresentation"
        ),
    ):
        provider.upsert(
            _representation(
                kind=RepresentationKind.DENSE,
            )
        )


@pytest.mark.parametrize(
    "representation_id",
    ("", "   "),
)
def test_empty_representation_id_is_rejected(
    representation_id: str,
) -> None:
    provider = InMemoryIndexProvider()

    with pytest.raises(
        ValueError,
        match="representation_id cannot be empty",
    ):
        provider.get(
            representation_id
        )


def test_non_string_representation_id_is_rejected() -> None:
    provider = InMemoryIndexProvider()

    with pytest.raises(
        TypeError,
        match="representation_id must be a string",
    ):
        provider.delete(
            123
        )


def test_membership_normalizes_representation_id() -> None:
    provider = InMemoryIndexProvider()
    representation = _representation()

    provider.upsert(
        representation
    )

    assert "  representation-001  " in provider


def test_invalid_membership_values_return_false() -> None:
    provider = InMemoryIndexProvider()

    assert "   " not in provider
    assert 123 not in provider
