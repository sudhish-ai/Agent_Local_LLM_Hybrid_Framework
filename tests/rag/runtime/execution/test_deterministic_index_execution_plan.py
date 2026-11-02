# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies deterministic V1 indexing behind the stable ALHF Knowledge
# Foundation index-execution boundary.
#
# Responsibilities:
# - Verify one configured logical index receives a representation.
# - Verify successful execution reports one logical index write.
# - Verify normalized index configuration.
# - Verify invalid construction and execution inputs are rejected.
#
# Must Not:
# - Test IndexingService or index-provider behavior in depth.
# - Define dynamic index routing or lifecycle intelligence.
# - Perform retrieval, Evidence, or Context construction.

from __future__ import annotations

import pytest

from alhf.rag.indexing.indexing_service import IndexingService
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
from alhf.rag.runtime.execution.deterministic_index_execution_plan import (
    DeterministicIndexExecutionPlan,
)
from alhf.rag.runtime.interfaces.knowledge_index_execution_plan import (
    KnowledgeIndexExecutionPlan,
)


def _representation() -> KnowledgeRepresentation:
    return KnowledgeRepresentation(
        representation_id="representation:test",
        knowledge_unit_ref="unit:test",
        derivation_id="derivation:test",
        knowledge_scope_ref="scope:test",
        resource_ref="resource:test",
        revision_ref="revision:test",
        kind=RepresentationKind.LEXICAL,
        payload=b"enterprise knowledge",
        media_type="text/plain",
        strategy_ref="provider:test",
        strategy_version="1.0",
    )


def _runtime() -> tuple[IndexingService, InMemoryIndexProvider]:
    provider = InMemoryIndexProvider()
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


def test_plan_satisfies_stable_execution_contract() -> None:
    service, _ = _runtime()

    plan = DeterministicIndexExecutionPlan(
        service=service,
        index_ref="knowledge-index",
    )

    assert isinstance(
        plan,
        KnowledgeIndexExecutionPlan,
    )


def test_execute_indexes_representation_and_reports_one_write() -> None:
    service, provider = _runtime()

    plan = DeterministicIndexExecutionPlan(
        service=service,
        index_ref="knowledge-index",
    )
    representation = _representation()

    write_count = plan.execute(
        representation
    )

    assert write_count == 1
    assert (
        provider.get("representation:test")
        is representation
    )


def test_index_ref_is_normalized() -> None:
    service, provider = _runtime()

    plan = DeterministicIndexExecutionPlan(
        service=service,
        index_ref="  knowledge-index  ",
    )

    assert plan.execute(
        _representation()
    ) == 1

    assert (
        provider.get("representation:test")
        is not None
    )


def test_rejects_invalid_service() -> None:
    with pytest.raises(
        TypeError,
        match="IndexingService",
    ):
        DeterministicIndexExecutionPlan(
            service=object(),  # type: ignore[arg-type]
            index_ref="knowledge-index",
        )


@pytest.mark.parametrize(
    "index_ref",
    ["", "   "],
)
def test_rejects_empty_index_ref(
    index_ref: str,
) -> None:
    service, _ = _runtime()

    with pytest.raises(
        ValueError,
        match="index_ref cannot be empty",
    ):
        DeterministicIndexExecutionPlan(
            service=service,
            index_ref=index_ref,
        )


def test_rejects_invalid_representation() -> None:
    service, _ = _runtime()

    plan = DeterministicIndexExecutionPlan(
        service=service,
        index_ref="knowledge-index",
    )

    with pytest.raises(
        TypeError,
        match="KnowledgeRepresentation",
    ):
        plan.execute(
            object(),  # type: ignore[arg-type]
        )
