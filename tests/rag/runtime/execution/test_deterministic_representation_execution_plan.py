# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies deterministic V1 representation execution behind the stable
# ALHF Knowledge Foundation representation fan-out boundary.
#
# Responsibilities:
# - Verify configured RepresentationService execution.
# - Verify one V1 representation is yielded incrementally.
# - Verify Knowledge Unit preservation through execution.
# - Verify invalid construction and execution inputs are rejected.
#
# Must Not:
# - Test representation-provider algorithms in depth.
# - Perform indexing, retrieval, Evidence, or Context construction.
# - Define future representation-selection intelligence.

from __future__ import annotations

from collections.abc import Iterator

import pytest

from alhf.rag.chunking.contracts.knowledge_unit import KnowledgeUnit
from alhf.rag.ingestion.contracts.canonical_content import CanonicalContentKind
from alhf.rag.ingestion.contracts.resource_identity import ResourceIdentity
from alhf.rag.representation.providers.deterministic_text_representation_provider import (
    DeterministicTextRepresentationProvider,
)
from alhf.rag.representation.providers.in_memory_representation_registry import (
    InMemoryRepresentationRegistry,
)
from alhf.rag.representation.representation_service import (
    RepresentationService,
)
from alhf.rag.runtime.execution.deterministic_representation_execution_plan import (
    DeterministicRepresentationExecutionPlan,
)
from alhf.rag.runtime.interfaces.knowledge_representation_execution_plan import (
    KnowledgeRepresentationExecutionPlan,
)


def _unit() -> KnowledgeUnit:
    identity = ResourceIdentity(
        knowledge_scope_ref="scope:test",
        source_ref="source:test",
        logical_resource_id="resource:test",
        revision_id="revision:test",
    )

    return KnowledgeUnit(
        unit_id="unit:test",
        identity=identity,
        canonical_artifact_ref="canonical:test",
        derivation_id="derivation:test",
        sequence=0,
        content=b"enterprise knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        strategy_ref="strategy:test",
        strategy_version="1.0",
    )


def _service() -> RepresentationService:
    registry = InMemoryRepresentationRegistry()
    registry.register(
        DeterministicTextRepresentationProvider()
    )

    return RepresentationService(
        registry=registry
    )


def test_plan_satisfies_stable_execution_contract() -> None:
    plan = DeterministicRepresentationExecutionPlan(
        service=_service()
    )

    assert isinstance(
        plan,
        KnowledgeRepresentationExecutionPlan,
    )


def test_execute_yields_one_v1_representation_incrementally() -> None:
    plan = DeterministicRepresentationExecutionPlan(
        service=_service()
    )

    results = plan.execute(
        _unit()
    )

    assert isinstance(results, Iterator)

    representations = tuple(results)

    assert len(representations) == 1
    assert representations[0].knowledge_unit_ref == "unit:test"
    assert representations[0].resource_ref == "resource:test"
    assert representations[0].revision_ref == "revision:test"
    assert representations[0].payload == b"enterprise knowledge"


def test_execute_is_deterministic() -> None:
    plan = DeterministicRepresentationExecutionPlan(
        service=_service()
    )
    unit = _unit()

    first = tuple(
        plan.execute(unit)
    )
    second = tuple(
        plan.execute(unit)
    )

    assert first == second


def test_rejects_invalid_service() -> None:
    with pytest.raises(
        TypeError,
        match="RepresentationService",
    ):
        DeterministicRepresentationExecutionPlan(
            service=object(),  # type: ignore[arg-type]
        )


def test_rejects_invalid_unit() -> None:
    plan = DeterministicRepresentationExecutionPlan(
        service=_service()
    )

    with pytest.raises(
        TypeError,
        match="KnowledgeUnit",
    ):
        next(
            plan.execute(
                object(),  # type: ignore[arg-type]
            )
        )
