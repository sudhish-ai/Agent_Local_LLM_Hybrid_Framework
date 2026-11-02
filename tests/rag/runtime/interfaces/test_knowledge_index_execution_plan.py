# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the stable index-execution fan-out boundary used by the ALHF
# Knowledge Foundation production ingestion runtime.
#
# Responsibilities:
# - Verify the interface cannot be instantiated directly.
# - Verify concrete plans satisfy the execution contract.
# - Verify representation input crosses the boundary unchanged.
# - Verify successful logical index-write counts can be returned.
#
# Must Not:
# - Define production index-routing policy.
# - Test physical index providers or registries.
# - Perform retrieval, Evidence, or Context construction.

from __future__ import annotations

import pytest

from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)
from alhf.rag.runtime.interfaces.knowledge_index_execution_plan import (
    KnowledgeIndexExecutionPlan,
)


class _TestPlan(KnowledgeIndexExecutionPlan):
    def __init__(
        self,
        write_count: int,
    ) -> None:
        self._write_count = write_count
        self.received: KnowledgeRepresentation | None = None

    def execute(
        self,
        representation: KnowledgeRepresentation,
    ) -> int:
        self.received = representation
        return self._write_count


def _representation() -> KnowledgeRepresentation:
    return KnowledgeRepresentation(
        representation_id="representation:test",
        knowledge_unit_ref="unit:test",
        derivation_id="derivation:test",
        knowledge_scope_ref="scope:test",
        resource_ref="resource:test",
        revision_ref="revision:test",
        kind=RepresentationKind.LEXICAL,
        payload=b"knowledge",
        media_type="text/plain",
        strategy_ref="provider:test",
        strategy_version="1.0",
    )


def test_interface_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        KnowledgeIndexExecutionPlan()


def test_concrete_plan_satisfies_contract() -> None:
    assert isinstance(
        _TestPlan(1),
        KnowledgeIndexExecutionPlan,
    )


def test_execute_preserves_representation_boundary() -> None:
    representation = _representation()
    plan = _TestPlan(1)

    write_count = plan.execute(
        representation
    )

    assert plan.received is representation
    assert write_count == 1


@pytest.mark.parametrize(
    "write_count",
    [0, 1, 2],
)
def test_execute_can_report_logical_write_count(
    write_count: int,
) -> None:
    plan = _TestPlan(
        write_count
    )

    assert (
        plan.execute(_representation())
        == write_count
    )


def test_interface_exposes_only_execute() -> None:
    assert (
        KnowledgeIndexExecutionPlan.__abstractmethods__
        == frozenset({"execute"})
    )
