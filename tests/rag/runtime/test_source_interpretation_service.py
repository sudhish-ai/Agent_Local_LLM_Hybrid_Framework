# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies source-neutral interpretation orchestration for the ALHF
# Knowledge Foundation production runtime.
#
# Problem Solved:
# Source interpretation orchestration must validate its boundaries while
# remaining independent from concrete source technologies and interpreters.
#
# Responsibilities:
# - Verify registry-based interpreter resolution.
# - Verify compatible interpreter invocation.
# - Verify governed KnowledgeSourcePlan delivery.
# - Verify invalid registry output rejection.
# - Verify incompatible resolved interpreter rejection.
# - Verify invalid interpreter output rejection.
# - Verify input and dependency contract validation.
#
# Must Not:
# - Test concrete local-source interpretation behavior.
# - Perform Knowledge acquisition or downstream ingestion.
# - Duplicate interpreter-registry implementation tests.
# - Test retrieval, Evidence, or evaluation.

from __future__ import annotations

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
from alhf.rag.runtime.source_interpretation_service import (
    SourceInterpretationService,
)


class _Interpreter(KnowledgeSourceInterpreter):
    interpreter_ref = "test-interpreter"
    interpreter_version = "1.0"

    def __init__(
        self,
        *,
        supported: bool = True,
        result: object | None = None,
    ) -> None:
        self._supported = supported
        self._result = result
        self.received_source: KnowledgeSourceInput | None = None

    def supports(
        self,
        source: KnowledgeSourceInput,
    ) -> bool:
        return self._supported

    def interpret(
        self,
        source: KnowledgeSourceInput,
    ) -> KnowledgeSourcePlan:
        self.received_source = source
        return self._result  # type: ignore[return-value]


class _Registry(KnowledgeSourceInterpreterRegistry):
    def __init__(
        self,
        result: object,
    ) -> None:
        self._result = result
        self.received_source: KnowledgeSourceInput | None = None

    def register(
        self,
        interpreter: KnowledgeSourceInterpreter,
    ) -> None:
        raise NotImplementedError

    def resolve(
        self,
        source: KnowledgeSourceInput,
    ) -> KnowledgeSourceInterpreter:
        self.received_source = source
        return self._result  # type: ignore[return-value]

    def contains(
        self,
        source: KnowledgeSourceInput,
    ) -> bool:
        return True


def _plan() -> KnowledgeSourcePlan:
    return KnowledgeSourcePlan(
        source_id="source:test",
        knowledge_scope_ref="scope:test",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="test-adapter",
    )


def test_interpret_resolves_invokes_and_returns_plan() -> None:
    plan = _plan()
    interpreter = _Interpreter(result=plan)
    registry = _Registry(interpreter)
    service = SourceInterpretationService(registry=registry)
    source = KnowledgeSourceInput(source="customer-source")

    result = service.interpret(source)

    assert result is plan
    assert registry.received_source is source
    assert interpreter.received_source is source


def test_constructor_rejects_wrong_registry_contract() -> None:
    with pytest.raises(
        TypeError,
        match="KnowledgeSourceInterpreterRegistry",
    ):
        SourceInterpretationService(
            registry=object(),  # type: ignore[arg-type]
        )


def test_interpret_rejects_wrong_source_contract() -> None:
    service = SourceInterpretationService(
        registry=_Registry(_Interpreter(result=_plan())),
    )

    with pytest.raises(TypeError, match="KnowledgeSourceInput"):
        service.interpret("source")  # type: ignore[arg-type]


def test_interpret_rejects_invalid_registry_output() -> None:
    service = SourceInterpretationService(
        registry=_Registry(object()),
    )

    with pytest.raises(
        TypeError,
        match="registry must return KnowledgeSourceInterpreter",
    ):
        service.interpret(
            KnowledgeSourceInput(source="customer-source"),
        )


def test_interpret_rejects_incompatible_resolved_interpreter() -> None:
    interpreter = _Interpreter(
        supported=False,
        result=_plan(),
    )
    service = SourceInterpretationService(
        registry=_Registry(interpreter),
    )

    with pytest.raises(
        ValueError,
        match="resolved interpreter does not support",
    ):
        service.interpret(
            KnowledgeSourceInput(source="customer-source"),
        )

    assert interpreter.received_source is None


def test_interpret_rejects_invalid_interpreter_output() -> None:
    interpreter = _Interpreter(
        result=object(),
    )
    service = SourceInterpretationService(
        registry=_Registry(interpreter),
    )

    with pytest.raises(
        TypeError,
        match="interpreter must return KnowledgeSourcePlan",
    ):
        service.interpret(
            KnowledgeSourceInput(source="customer-source"),
        )


def test_registry_resolution_failure_propagates() -> None:
    class _FailingRegistry(_Registry):
        def resolve(
            self,
            source: KnowledgeSourceInput,
        ) -> KnowledgeSourceInterpreter:
            raise LookupError("no compatible interpreter")

    service = SourceInterpretationService(
        registry=_FailingRegistry(object()),
    )

    with pytest.raises(
        LookupError,
        match="no compatible interpreter",
    ):
        service.interpret(
            KnowledgeSourceInput(source="customer-source"),
        )


def test_interpreter_failure_propagates() -> None:
    class _FailingInterpreter(_Interpreter):
        def interpret(
            self,
            source: KnowledgeSourceInput,
        ) -> KnowledgeSourcePlan:
            raise RuntimeError("interpretation failed")

    service = SourceInterpretationService(
        registry=_Registry(_FailingInterpreter()),
    )

    with pytest.raises(
        RuntimeError,
        match="interpretation failed",
    ):
        service.interpret(
            KnowledgeSourceInput(source="customer-source"),
        )
