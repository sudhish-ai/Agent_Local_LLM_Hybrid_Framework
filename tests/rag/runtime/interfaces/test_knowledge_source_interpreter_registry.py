# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the stable Knowledge source interpreter registry boundary.
#
# Responsibilities:
# - Prove the registry remains an abstract capability boundary.
# - Prove concrete registries can register source interpreters.
# - Prove compatible interpreters can be resolved by source input.
# - Prove source capability checks remain behind the registry.
# - Protect runtime callers from source-technology-specific branching.
#
# Must Not:
# - Access real customer sources.
# - Perform Knowledge acquisition or parsing.
# - Configure downstream Knowledge processing.
# - Introduce Standard RAG, GraphRAG, or Agentic RAG semantics.

import pytest

from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSourceKind,
)
from alhf.rag.runtime.contracts.knowledge_source_input import (
    KnowledgeSourceInput,
)
from alhf.rag.runtime.contracts.knowledge_source_plan import (
    KnowledgeSourcePlan,
)
from alhf.rag.runtime.interfaces.knowledge_source_interpreter import (
    KnowledgeSourceInterpreter,
)
from alhf.rag.runtime.interfaces.knowledge_source_interpreter_registry import (
    KnowledgeSourceInterpreterRegistry,
)


class _TestInterpreter(
    KnowledgeSourceInterpreter
):
    """Minimal source interpreter used for interface validation."""

    @property
    def interpreter_ref(self) -> str:
        return "test-interpreter"

    @property
    def interpreter_version(self) -> str:
        return "1.0"

    def supports(
        self,
        source: KnowledgeSourceInput,
    ) -> bool:
        return (
            isinstance(
                source,
                KnowledgeSourceInput,
            )
            and source.source.startswith(
                "test:"
            )
        )

    def interpret(
        self,
        source: KnowledgeSourceInput,
    ) -> KnowledgeSourcePlan:
        if not self.supports(
            source
        ):
            raise ValueError(
                "unsupported source"
            )

        return KnowledgeSourcePlan(
            source_id="source-001",
            knowledge_scope_ref="scope-001",
            source_kind=KnowledgeSourceKind.FILE,
            adapter_ref="test-adapter",
        )


class _TestRegistry(
    KnowledgeSourceInterpreterRegistry
):
    """Minimal registry implementation used to validate the interface."""

    def __init__(
        self,
    ) -> None:
        self._interpreters: list[
            KnowledgeSourceInterpreter
        ] = []

    def register(
        self,
        interpreter: KnowledgeSourceInterpreter,
    ) -> None:
        if not isinstance(
            interpreter,
            KnowledgeSourceInterpreter,
        ):
            raise TypeError(
                "interpreter must be an instance of "
                "KnowledgeSourceInterpreter"
            )

        self._interpreters.append(
            interpreter
        )

    def resolve(
        self,
        source: KnowledgeSourceInput,
    ) -> KnowledgeSourceInterpreter:
        if not isinstance(
            source,
            KnowledgeSourceInput,
        ):
            raise TypeError(
                "source must be an instance of "
                "KnowledgeSourceInput"
            )

        for interpreter in self._interpreters:
            if interpreter.supports(
                source
            ):
                return interpreter

        raise LookupError(
            "source interpreter not found"
        )

    def contains(
        self,
        source: KnowledgeSourceInput,
    ) -> bool:
        if not isinstance(
            source,
            KnowledgeSourceInput,
        ):
            raise TypeError(
                "source must be an instance of "
                "KnowledgeSourceInput"
            )

        return any(
            interpreter.supports(
                source
            )
            for interpreter in self._interpreters
        )


def test_registry_interface_cannot_be_instantiated() -> None:
    with pytest.raises(
        TypeError
    ):
        KnowledgeSourceInterpreterRegistry()


def test_concrete_registry_is_registry_contract() -> None:
    registry = _TestRegistry()

    assert isinstance(
        registry,
        KnowledgeSourceInterpreterRegistry,
    )


def test_registered_interpreter_can_be_resolved() -> None:
    registry = _TestRegistry()
    interpreter = _TestInterpreter()

    registry.register(
        interpreter
    )

    resolved = registry.resolve(
        KnowledgeSourceInput(
            source="test:source"
        )
    )

    assert resolved is interpreter


def test_contains_reports_compatible_interpreter() -> None:
    registry = _TestRegistry()

    registry.register(
        _TestInterpreter()
    )

    assert registry.contains(
        KnowledgeSourceInput(
            source="test:source"
        )
    ) is True


def test_contains_reports_missing_capability() -> None:
    registry = _TestRegistry()

    registry.register(
        _TestInterpreter()
    )

    assert registry.contains(
        KnowledgeSourceInput(
            source="unsupported:source"
        )
    ) is False


def test_resolve_reports_missing_capability() -> None:
    registry = _TestRegistry()

    registry.register(
        _TestInterpreter()
    )

    with pytest.raises(
        LookupError,
        match="source interpreter not found",
    ):
        registry.resolve(
            KnowledgeSourceInput(
                source="unsupported:source"
            )
        )


def test_register_rejects_wrong_contract_type() -> None:
    registry = _TestRegistry()

    with pytest.raises(
        TypeError,
        match=(
            "interpreter must be an instance of "
            "KnowledgeSourceInterpreter"
        ),
    ):
        registry.register(
            "interpreter"
        )


def test_resolve_rejects_wrong_source_contract() -> None:
    registry = _TestRegistry()

    registry.register(
        _TestInterpreter()
    )

    with pytest.raises(
        TypeError,
        match=(
            "source must be an instance of "
            "KnowledgeSourceInput"
        ),
    ):
        registry.resolve(
            "test:source"
        )


def test_registry_resolution_preserves_source_only_customer_boundary() -> None:
    registry = _TestRegistry()

    registry.register(
        _TestInterpreter()
    )

    source = KnowledgeSourceInput(
        source="test:source"
    )

    interpreter = registry.resolve(
        source
    )

    plan = interpreter.interpret(
        source
    )

    assert source.source == "test:source"
    assert plan.adapter_ref == "test-adapter"
    assert not hasattr(
        source,
        "adapter_ref",
    )
    assert not hasattr(
        source,
        "parser",
    )
    assert not hasattr(
        source,
        "rag_type",
    )
