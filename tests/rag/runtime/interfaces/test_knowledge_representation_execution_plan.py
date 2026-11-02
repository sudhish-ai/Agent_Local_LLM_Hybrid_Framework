# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the stable representation-execution fan-out boundary used by
# the ALHF Knowledge Foundation production ingestion runtime.
#
# Responsibilities:
# - Verify the interface cannot be instantiated directly.
# - Verify concrete execution plans satisfy the interface contract.
# - Verify one Knowledge Unit can yield multiple representations.
# - Verify representation delivery remains incremental.
#
# Must Not:
# - Define production representation-selection policy.
# - Test concrete representation providers or registries.
# - Perform indexing, retrieval, Evidence, or Context construction.

from __future__ import annotations

from collections.abc import Iterator

import pytest

from alhf.rag.chunking.contracts.knowledge_unit import KnowledgeUnit
from alhf.rag.ingestion.contracts.canonical_content import CanonicalContentKind
from alhf.rag.ingestion.contracts.resource_identity import ResourceIdentity
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)
from alhf.rag.runtime.interfaces.knowledge_representation_execution_plan import (
    KnowledgeRepresentationExecutionPlan,
)


class _TestPlan(KnowledgeRepresentationExecutionPlan):
    def __init__(
        self,
        representations: tuple[KnowledgeRepresentation, ...],
    ) -> None:
        self._representations = representations
        self.received_unit: KnowledgeUnit | None = None

    def execute(
        self,
        unit: KnowledgeUnit,
    ) -> Iterator[KnowledgeRepresentation]:
        self.received_unit = unit
        yield from self._representations


def _identity() -> ResourceIdentity:
    return ResourceIdentity(
        knowledge_scope_ref="scope:test",
        source_ref="source:test",
        logical_resource_id="resource:test",
        revision_id="revision:test",
    )


def _unit() -> KnowledgeUnit:
    return KnowledgeUnit(
        unit_id="unit:test",
        identity=_identity(),
        canonical_artifact_ref="canonical:test",
        derivation_id="derivation:test",
        sequence=0,
        content=b"knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        strategy_ref="strategy:test",
        strategy_version="1.0",
    )


def _representation(
    representation_id: str,
    kind: RepresentationKind,
) -> KnowledgeRepresentation:
    return KnowledgeRepresentation(
        representation_id=representation_id,
        knowledge_unit_ref="unit:test",
        derivation_id="derivation:test",
        knowledge_scope_ref="scope:test",
        resource_ref="resource:test",
        revision_ref="revision:test",
        kind=kind,
        payload=b"representation",
        media_type="application/octet-stream",
        strategy_ref="provider:test",
        strategy_version="1.0",
    )


def test_interface_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        KnowledgeRepresentationExecutionPlan()


def test_concrete_plan_satisfies_contract() -> None:
    assert isinstance(
        _TestPlan(()),
        KnowledgeRepresentationExecutionPlan,
    )


def test_execute_preserves_unit_and_is_incremental() -> None:
    unit = _unit()
    plan = _TestPlan(())
    results = plan.execute(unit)

    assert isinstance(results, Iterator)
    assert tuple(results) == ()
    assert plan.received_unit is unit


def test_execute_can_yield_multiple_representations() -> None:
    lexical = _representation(
        "representation:lexical",
        RepresentationKind.LEXICAL,
    )
    dense = _representation(
        "representation:dense",
        RepresentationKind.DENSE,
    )
    plan = _TestPlan((lexical, dense))

    assert tuple(
        plan.execute(_unit())
    ) == (
        lexical,
        dense,
    )


def test_interface_exposes_only_execute() -> None:
    assert (
        KnowledgeRepresentationExecutionPlan.__abstractmethods__
        == frozenset({"execute"})
    )
