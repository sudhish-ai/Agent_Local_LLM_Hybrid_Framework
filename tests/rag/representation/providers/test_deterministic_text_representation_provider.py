# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF DeterministicTextRepresentationProvider.
#
# Responsibilities:
# - Validate stable provider identity and version.
# - Validate text Knowledge Unit compatibility.
# - Validate deterministic lexical representation generation.
# - Validate Knowledge Unit and derivation provenance preservation.
# - Validate Knowledge scope, resource, and revision provenance.
# - Validate deterministic representation identity.
# - Validate payload and representation-kind semantics.
# - Validate unsupported and invalid Knowledge Unit rejection.
#
# Must Not:
# - Test dense embedding generation.
# - Test external representation models.
# - Test vector-store-specific behavior.
# - Test indexing, retrieval, reranking, or context construction.
# - Test Representation Intelligence or adaptive provider selection.
# - Test concurrency, batching, or NFT execution strategies.
# - Depend on LangChain, LangGraph, or external frameworks.

import pytest

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContentKind,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)
from alhf.rag.representation.providers.deterministic_text_representation_provider import (
    DeterministicTextRepresentationProvider,
)


def _unit(
    *,
    content: bytes = b"enterprise knowledge",
    content_kind: CanonicalContentKind = CanonicalContentKind.TEXT,
    media_type: str = "text/plain",
) -> KnowledgeUnit:
    return KnowledgeUnit(
        unit_id="unit-001",
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        canonical_artifact_ref="canonical-001",
        derivation_id="derivation-001",
        sequence=0,
        content=content,
        content_kind=content_kind,
        media_type=media_type,
        strategy_ref="text-derivation",
        strategy_version="1.0",
    )


def _provider() -> DeterministicTextRepresentationProvider:
    return DeterministicTextRepresentationProvider()


def test_provider_exposes_stable_identity() -> None:
    provider = _provider()

    assert provider.provider_ref == (
        "deterministic-text-representation"
    )
    assert provider.provider_version == "1.0"


def test_provider_supports_text_knowledge_unit() -> None:
    provider = _provider()

    assert provider.supports(
        _unit()
    ) is True


def test_provider_supports_normalized_text_media_type() -> None:
    provider = _provider()

    assert provider.supports(
        _unit(
            media_type="  TEXT/PLAIN  ",
        )
    ) is True


def test_provider_rejects_non_text_content_kind() -> None:
    provider = _provider()

    assert provider.supports(
        _unit(
            content_kind=CanonicalContentKind.STRUCTURED,
        )
    ) is False


def test_provider_rejects_non_text_media_type() -> None:
    provider = _provider()

    assert provider.supports(
        _unit(
            media_type="application/json",
        )
    ) is False


def test_supports_returns_false_for_invalid_object() -> None:
    provider = _provider()

    assert provider.supports(
        "invalid-unit"
    ) is False


def test_represent_returns_knowledge_representation() -> None:
    representation = _provider().represent(
        _unit()
    )

    assert isinstance(
        representation,
        KnowledgeRepresentation,
    )


def test_represent_produces_lexical_representation() -> None:
    representation = _provider().represent(
        _unit()
    )

    assert representation.kind == RepresentationKind.LEXICAL


def test_represent_preserves_knowledge_unit_reference() -> None:
    unit = _unit()

    representation = _provider().represent(
        unit
    )

    assert representation.knowledge_unit_ref == unit.unit_id


def test_represent_preserves_derivation_identity() -> None:
    unit = _unit()

    representation = _provider().represent(
        unit
    )

    assert representation.derivation_id == unit.derivation_id


def test_represent_preserves_knowledge_scope() -> None:
    representation = _provider().represent(
        _unit()
    )

    assert representation.knowledge_scope_ref == "scope-001"


def test_represent_preserves_resource_provenance() -> None:
    representation = _provider().represent(
        _unit()
    )

    assert representation.resource_ref == "resource-001"
    assert representation.revision_ref == "revision-001"


def test_represent_preserves_unit_content_as_payload() -> None:
    content = b"deterministic enterprise knowledge"

    representation = _provider().represent(
        _unit(
            content=content,
        )
    )

    assert representation.payload == content


def test_represent_uses_text_media_type() -> None:
    representation = _provider().represent(
        _unit()
    )

    assert representation.media_type == "text/plain"


def test_represent_records_provider_identity() -> None:
    provider = _provider()

    representation = provider.represent(
        _unit()
    )

    assert representation.strategy_ref == provider.provider_ref
    assert representation.strategy_version == provider.provider_version


def test_deterministic_provider_has_no_model_identity() -> None:
    representation = _provider().represent(
        _unit()
    )

    assert representation.model_ref is None
    assert representation.model_version is None


def test_representation_identity_is_deterministic() -> None:
    provider = _provider()
    unit = _unit()

    first = provider.represent(
        unit
    )
    second = provider.represent(
        unit
    )

    assert first.representation_id == second.representation_id


def test_different_unit_identity_changes_representation_identity() -> None:
    provider = _provider()

    first = provider.represent(
        _unit()
    )

    second_unit = KnowledgeUnit(
        unit_id="unit-002",
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        canonical_artifact_ref="canonical-001",
        derivation_id="derivation-001",
        sequence=1,
        content=b"enterprise knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        strategy_ref="text-derivation",
        strategy_version="1.0",
    )

    second = provider.represent(
        second_unit
    )

    assert first.representation_id != second.representation_id


def test_representation_identity_has_expected_prefix() -> None:
    representation = _provider().represent(
        _unit()
    )

    assert representation.representation_id.startswith(
        "representation:"
    )


def test_empty_text_payload_is_supported() -> None:
    representation = _provider().represent(
        _unit(
            content=b"",
        )
    )

    assert representation.payload == b""
    assert representation.size_bytes == 0


def test_invalid_unit_is_rejected() -> None:
    provider = _provider()

    with pytest.raises(
        TypeError,
        match="unit must be an instance of KnowledgeUnit",
    ):
        provider.represent(
            "invalid-unit"
        )


def test_unsupported_content_kind_is_rejected() -> None:
    provider = _provider()

    with pytest.raises(
        ValueError,
        match=(
            "DeterministicTextRepresentationProvider "
            "requires a text Knowledge Unit"
        ),
    ):
        provider.represent(
            _unit(
                content_kind=CanonicalContentKind.STRUCTURED,
            )
        )


def test_unsupported_media_type_is_rejected() -> None:
    provider = _provider()

    with pytest.raises(
        ValueError,
        match=(
            "DeterministicTextRepresentationProvider "
            "requires a text Knowledge Unit"
        ),
    ):
        provider.represent(
            _unit(
                media_type="application/json",
            )
        )
