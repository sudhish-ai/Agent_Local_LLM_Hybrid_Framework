# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides source-neutral interpretation orchestration for the ALHF
# Knowledge Foundation production runtime.
#
# Problem Solved:
# Minimal customer Knowledge source input must become a governed internal
# source plan without coupling runtime orchestration to local files,
# cloud systems, databases, APIs, or future source technologies.
#
# Responsibilities:
# - Accept one minimal KnowledgeSourceInput.
# - Resolve a compatible interpreter through the interpreter registry.
# - Validate resolved interpreter compatibility.
# - Delegate source interpretation to KnowledgeSourceInterpreter.
# - Validate the governed KnowledgeSourcePlan returned by the interpreter.
# - Preserve separation between customer input and ingestion mechanics.
#
# Must Not:
# - Inspect or acquire Knowledge content.
# - Contain source-technology-specific branching.
# - Construct source plans directly.
# - Select acquisition adapters, parsers, or downstream providers.
# - Execute ingestion, indexing, retrieval, or evaluation.
# - Implement source-selection intelligence or execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Common source-interpretation orchestration boundary of the runtime.
# - Connects KnowledgeSourceInput to dynamically resolved interpreters.
# - Produces governed KnowledgeSourcePlan for ingestion execution.
#
# Future Extensibility:
# - New source technologies require no service changes.
# - Interpreter registries can evolve selection policy independently.
# - Profile and capability intelligence can compose above this boundary.
# - Local, cloud, hybrid, and future interpreters remain interchangeable.

from __future__ import annotations

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


class SourceInterpretationService:
    """Source-neutral orchestration for governed source interpretation."""

    def __init__(
        self,
        *,
        registry: KnowledgeSourceInterpreterRegistry,
    ) -> None:
        if not isinstance(
            registry,
            KnowledgeSourceInterpreterRegistry,
        ):
            raise TypeError(
                "registry must be an instance of "
                "KnowledgeSourceInterpreterRegistry"
            )

        self._registry = registry

    def interpret(
        self,
        source: KnowledgeSourceInput,
    ) -> KnowledgeSourcePlan:
        """Resolve and invoke a compatible source interpreter."""

        if not isinstance(
            source,
            KnowledgeSourceInput,
        ):
            raise TypeError(
                "source must be an instance of KnowledgeSourceInput"
            )

        interpreter = self._registry.resolve(
            source,
        )

        self._validate_interpreter(
            interpreter=interpreter,
            source=source,
        )

        plan = interpreter.interpret(
            source,
        )

        self._validate_result(
            plan,
        )

        return plan

    @staticmethod
    def _validate_interpreter(
        *,
        interpreter: KnowledgeSourceInterpreter,
        source: KnowledgeSourceInput,
    ) -> None:
        """Validate registry output and interpreter compatibility."""

        if not isinstance(
            interpreter,
            KnowledgeSourceInterpreter,
        ):
            raise TypeError(
                "registry must return KnowledgeSourceInterpreter"
            )

        if not interpreter.supports(
            source,
        ):
            raise ValueError(
                "resolved interpreter does not support "
                "Knowledge source input"
            )

    @staticmethod
    def _validate_result(
        plan: KnowledgeSourcePlan,
    ) -> None:
        """Validate the governed source plan returned by interpretation."""

        if not isinstance(
            plan,
            KnowledgeSourcePlan,
        ):
            raise TypeError(
                "interpreter must return KnowledgeSourcePlan"
            )
