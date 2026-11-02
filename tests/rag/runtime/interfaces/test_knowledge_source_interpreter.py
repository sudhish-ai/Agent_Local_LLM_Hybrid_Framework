# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the stable ALHF KnowledgeSourceInterpreter runtime boundary.
#
# Responsibilities:
# - Prove interpreter identity is implementation-owned.
# - Prove source compatibility remains behind the interface.
# - Prove interpretation returns a governed KnowledgeSourcePlan.
# - Protect the boundary from acquisition and RAG implementation details.
#
# Must Not:
# - Access real customer sources.
# - Perform acquisition or parsing.
# - Configure derivation, representation, indexing, or retrieval.
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


class _TestSourceInterpreter(
    KnowledgeSourceInterpreter
):
    """Minimal implementation used to validate the interface contract."""

    @property
    def interpreter_ref(self) -> str:
        return "test-source-interpreter"

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
            and source.source.startswith("local:")
        )

    def interpret(
        self,
        source: KnowledgeSourceInput,
    ) -> KnowledgeSourcePlan:
        if not isinstance(
            source,
            KnowledgeSourceInput,
        ):
            raise TypeError(
                "source must be an instance of "
                "KnowledgeSourceInput"
            )

        if not self.supports(
            source
        ):
            raise ValueError(
                "unsupported Knowledge source input"
            )

        return KnowledgeSourcePlan(
            source_id="source-001",
            knowledge_scope_ref="scope-001",
            source_kind=KnowledgeSourceKind.FILE,
            adapter_ref="local-file",
        )


def test_interface_cannot_be_instantiated() -> None:
    with pytest.raises(
        TypeError
    ):
        KnowledgeSourceInterpreter()


def test_concrete_interpreter_exposes_stable_identity() -> None:
    interpreter = _TestSourceInterpreter()

    assert (
        interpreter.interpreter_ref
        == "test-source-interpreter"
    )
    assert interpreter.interpreter_version == "1.0"


def test_concrete_interpreter_declares_source_support() -> None:
    interpreter = _TestSourceInterpreter()

    supported = KnowledgeSourceInput(
        source="local:D:/CompanyKnowledge"
    )

    unsupported = KnowledgeSourceInput(
        source="https://knowledge.example/source"
    )

    assert interpreter.supports(
        supported
    ) is True

    assert interpreter.supports(
        unsupported
    ) is False


def test_interpret_returns_governed_source_plan() -> None:
    interpreter = _TestSourceInterpreter()

    result = interpreter.interpret(
        KnowledgeSourceInput(
            source="local:D:/CompanyKnowledge"
        )
    )

    assert isinstance(
        result,
        KnowledgeSourcePlan,
    )
    assert result.source_id == "source-001"
    assert result.knowledge_scope_ref == "scope-001"
    assert result.source_kind == KnowledgeSourceKind.FILE
    assert result.adapter_ref == "local-file"


def test_interpret_rejects_wrong_contract_type() -> None:
    interpreter = _TestSourceInterpreter()

    with pytest.raises(
        TypeError,
        match=(
            "source must be an instance of "
            "KnowledgeSourceInput"
        ),
    ):
        interpreter.interpret(
            "local:D:/CompanyKnowledge"
        )


def test_interpret_rejects_unsupported_source() -> None:
    interpreter = _TestSourceInterpreter()

    with pytest.raises(
        ValueError,
        match="unsupported Knowledge source input",
    ):
        interpreter.interpret(
            KnowledgeSourceInput(
                source="https://knowledge.example/source"
            )
        )


def test_interpreter_changes_do_not_change_customer_contract() -> None:
    source = KnowledgeSourceInput(
        source="local:D:/CompanyKnowledge"
    )

    result = _TestSourceInterpreter().interpret(
        source
    )

    assert source.source == "local:D:/CompanyKnowledge"
    assert result.adapter_ref == "local-file"


def test_source_plan_contains_no_downstream_rag_configuration() -> None:
    plan = _TestSourceInterpreter().interpret(
        KnowledgeSourceInput(
            source="local:D:/CompanyKnowledge"
        )
    )

    assert not hasattr(
        plan,
        "parser",
    )
    assert not hasattr(
        plan,
        "chunk_size",
    )
    assert not hasattr(
        plan,
        "embedding_model",
    )
    assert not hasattr(
        plan,
        "index_ref",
    )
    assert not hasattr(
        plan,
        "retrieval_strategy",
    )
    assert not hasattr(
        plan,
        "rag_type",
    )
