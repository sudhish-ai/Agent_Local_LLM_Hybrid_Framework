# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF RepresentationProvider interface.
#
# Responsibilities:
# - Validate the abstract representation-provider boundary.
# - Validate provider identity and version contracts.
# - Validate Knowledge Unit compatibility declaration.
# - Validate KnowledgeRepresentation production.
# - Validate Knowledge Unit and derivation provenance preservation.
# - Validate Knowledge scope, resource, and revision preservation.
# - Protect Knowledge semantics from representation technology.
#
# Must Not:
# - Test concrete embedding models.
# - Test vector-store-specific behavior.
# - Test indexing, retrieval, reranking, or context construction.
# - Test Representation Intelligence or provider selection.
# - Test concurrency, batching, or NFT execution strategies.
# - Depend on external RAG or orchestration frameworks.

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
from alhf.rag.representation.interfaces.representation_provider import (
    RepresentationProvider,
)


class StubRepresentationProvider(RepresentationProvider):
    """Minimal provider used to validate the universal boundary."""

    @property
    def provider_ref(self) -> str:
        return "stub-dense-provider"

    @property
    def provider_version(self) -> str:
        return "1.0"

    def supports(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        return unit.content_kind == CanonicalContentKind.TEXT

    def represent(
        self,
        unit: KnowledgeUnit,
    ) -> KnowledgeRepresentation:
        return KnowledgeRepresentation(
            representation_id="representation-001",
            knowledge_unit_ref=unit.unit_id,
            derivation_id=unit.derivation_id,
            knowledge_scope_ref=unit.knowledge_scope_ref,
            resource_ref=unit.resource_ref,
            revision_ref=unit.revision_ref,
            kind=RepresentationKind.DENSE,
            payload=b"dense-payload",
            media_type="application/octet-stream",
            strategy_ref=self.provider_ref,
            strategy_version=self.provider_version,
            model_ref="test-model",
            model_version="1.0",
        )


class MissingRepresentProvider(RepresentationProvider):
    """Invalid provider missing representation behavior."""

    @property
    def provider_ref(self) -> str:
        return "missing-represent"

    @property
    def provider_version(self) -> str:
        return "1.0"

    def supports(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        return True


class MissingSupportsProvider(RepresentationProvider):
    """Invalid provider missing compatibility behavior."""

    @property
    def provider_ref(self) -> str:
        return "missing-supports"

    @property
    def provider_version(self) -> str:
        return "1.0"

    def represent(
        self,
        unit: KnowledgeUnit,
    ) -> KnowledgeRepresentation:
        raise NotImplementedError


def _unit() -> KnowledgeUnit:
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
        content=b"enterprise knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        strategy_ref="text-derivation",
        strategy_version="1.0",
    )


def test_representation_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        RepresentationProvider()


def test_missing_represent_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingRepresentProvider()


def test_missing_supports_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingSupportsProvider()


def test_concrete_provider_can_be_instantiated() -> None:
    provider = StubRepresentationProvider()

    assert isinstance(
        provider,
        RepresentationProvider,
    )


def test_provider_exposes_stable_reference() -> None:
    provider = StubRepresentationProvider()

    assert provider.provider_ref == "stub-dense-provider"


def test_provider_exposes_stable_version() -> None:
    provider = StubRepresentationProvider()

    assert provider.provider_version == "1.0"


def test_provider_supports_text_knowledge_unit() -> None:
    provider = StubRepresentationProvider()

    assert provider.supports(
        _unit()
    ) is True


def test_represent_returns_knowledge_representation() -> None:
    provider = StubRepresentationProvider()

    representation = provider.represent(
        _unit()
    )

    assert isinstance(
        representation,
        KnowledgeRepresentation,
    )


def test_represent_preserves_knowledge_unit_reference() -> None:
    provider = StubRepresentationProvider()
    unit = _unit()

    representation = provider.represent(
        unit
    )

    assert representation.knowledge_unit_ref == unit.unit_id


def test_represent_preserves_derivation_identity() -> None:
    provider = StubRepresentationProvider()
    unit = _unit()

    representation = provider.represent(
        unit
    )

    assert representation.derivation_id == unit.derivation_id


def test_represent_preserves_knowledge_scope() -> None:
    representation = StubRepresentationProvider().represent(
        _unit()
    )

    assert representation.knowledge_scope_ref == "scope-001"


def test_represent_preserves_resource_identity() -> None:
    representation = StubRepresentationProvider().represent(
        _unit()
    )

    assert representation.resource_ref == "resource-001"
    assert representation.revision_ref == "revision-001"


def test_represent_records_representation_kind() -> None:
    representation = StubRepresentationProvider().represent(
        _unit()
    )

    assert representation.kind == RepresentationKind.DENSE


def test_represent_records_provider_identity() -> None:
    provider = StubRepresentationProvider()

    representation = provider.represent(
        _unit()
    )

    assert representation.strategy_ref == provider.provider_ref
    assert representation.strategy_version == provider.provider_version


def test_represent_records_model_identity() -> None:
    representation = StubRepresentationProvider().represent(
        _unit()
    )

    assert representation.model_ref == "test-model"
    assert representation.model_version == "1.0"


def test_represent_preserves_provider_payload() -> None:
    representation = StubRepresentationProvider().represent(
        _unit()
    )

    assert representation.payload == b"dense-payload"
