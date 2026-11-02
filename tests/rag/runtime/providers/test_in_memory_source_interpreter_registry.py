# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the production in-memory registry for ALHF Knowledge source
# interpreters.
#
# Problem Solved:
# Source interpretation must remain deterministic, validated, extensible,
# and independent from source-technology-specific runtime branching.
#
# Responsibilities:
# - Verify interpreter registration and identity validation.
# - Verify deterministic registration-order capability resolution.
# - Verify compatible-source availability checks.
# - Verify duplicate interpreter rejection.
# - Verify invalid contract and source rejection.
# - Verify reference membership and registry size behavior.
#
# Must Not:
# - Test Knowledge acquisition or parsing.
# - Perform source-specific production orchestration.
# - Duplicate LocalSourceInterpreter behavior tests.
# - Test retrieval or downstream Knowledge execution.

from __future__ import annotations

import pytest

from alhf.rag.runtime.contracts.knowledge_source_input import (
    KnowledgeSourceInput,
)
from alhf.rag.runtime.contracts.knowledge_source_plan import (
    KnowledgeSourcePlan,
)
from alhf.rag.runtime.interfaces.knowledge_source_interpreter import (
    KnowledgeSourceInterpreter,
)
from alhf.rag.runtime.providers.in_memory_source_interpreter_registry import (
    InMemorySourceInterpreterRegistry,
)


class _Interpreter(KnowledgeSourceInterpreter):
    def __init__(
        self,
        *,
        interpreter_ref: str,
        interpreter_version: str = "1.0",
        supported_source: str = "supported",
    ) -> None:
        self._interpreter_ref = interpreter_ref
        self._interpreter_version = interpreter_version
        self._supported_source = supported_source

    @property
    def interpreter_ref(self) -> str:
        return self._interpreter_ref

    @property
    def interpreter_version(self) -> str:
        return self._interpreter_version

    def supports(
        self,
        source: KnowledgeSourceInput,
    ) -> bool:
        return source.source == self._supported_source

    def interpret(
        self,
        source: KnowledgeSourceInput,
    ) -> KnowledgeSourcePlan:
        raise NotImplementedError


def test_registers_interpreter_and_tracks_registry_size() -> None:
    registry = InMemorySourceInterpreterRegistry()
    interpreter = _Interpreter(interpreter_ref="test-interpreter")

    registry.register(interpreter)

    assert len(registry) == 1
    assert "test-interpreter" in registry


def test_resolve_returns_compatible_interpreter() -> None:
    registry = InMemorySourceInterpreterRegistry()
    interpreter = _Interpreter(interpreter_ref="test-interpreter")
    registry.register(interpreter)

    result = registry.resolve(KnowledgeSourceInput(source="supported"))

    assert result is interpreter


def test_resolve_preserves_registration_order() -> None:
    registry = InMemorySourceInterpreterRegistry()
    first = _Interpreter(interpreter_ref="first")
    second = _Interpreter(interpreter_ref="second")

    registry.register(first)
    registry.register(second)

    result = registry.resolve(KnowledgeSourceInput(source="supported"))

    assert result is first


def test_contains_reports_compatible_capability() -> None:
    registry = InMemorySourceInterpreterRegistry()
    registry.register(_Interpreter(interpreter_ref="test-interpreter"))

    assert registry.contains(KnowledgeSourceInput(source="supported"))
    assert not registry.contains(KnowledgeSourceInput(source="unsupported"))


def test_resolve_rejects_missing_capability() -> None:
    registry = InMemorySourceInterpreterRegistry()

    with pytest.raises(
        LookupError,
        match="source interpreter not found",
    ):
        registry.resolve(KnowledgeSourceInput(source="unsupported"))


def test_register_rejects_wrong_contract() -> None:
    registry = InMemorySourceInterpreterRegistry()

    with pytest.raises(TypeError, match="KnowledgeSourceInterpreter"):
        registry.register(object())  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("interpreter_ref", "interpreter_version", "expected"),
    [
        ("", "1.0", "interpreter_ref cannot be empty"),
        ("   ", "1.0", "interpreter_ref cannot be empty"),
        ("valid", "", "interpreter_version cannot be empty"),
        ("valid", "   ", "interpreter_version cannot be empty"),
    ],
)
def test_register_rejects_empty_identity(
    interpreter_ref: str,
    interpreter_version: str,
    expected: str,
) -> None:
    registry = InMemorySourceInterpreterRegistry()
    interpreter = _Interpreter(
        interpreter_ref=interpreter_ref,
        interpreter_version=interpreter_version,
    )

    with pytest.raises(ValueError, match=expected):
        registry.register(interpreter)


def test_register_rejects_duplicate_normalized_reference() -> None:
    registry = InMemorySourceInterpreterRegistry()
    registry.register(_Interpreter(interpreter_ref="duplicate"))

    with pytest.raises(
        ValueError,
        match="interpreter already registered: duplicate",
    ):
        registry.register(_Interpreter(interpreter_ref=" duplicate "))


def test_resolution_rejects_wrong_source_contract() -> None:
    registry = InMemorySourceInterpreterRegistry()

    with pytest.raises(TypeError, match="KnowledgeSourceInput"):
        registry.resolve("source")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="KnowledgeSourceInput"):
        registry.contains("source")  # type: ignore[arg-type]


def test_membership_is_safe_for_invalid_references() -> None:
    registry = InMemorySourceInterpreterRegistry()
    registry.register(_Interpreter(interpreter_ref="registered"))

    assert " registered " in registry
    assert "" not in registry
    assert "   " not in registry
    assert object() not in registry
    assert "missing" not in registry
