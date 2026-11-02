# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the in-memory source-interpreter registry used by the ALHF
# Knowledge Foundation production runtime.
#
# Problem Solved:
# Runtime source interpretation must resolve compatible interpreters
# without hard-coded source technologies, provider conditionals, or
# technical source configuration in the customer-facing runtime.
#
# Responsibilities:
# - Register configured KnowledgeSourceInterpreter implementations.
# - Preserve deterministic interpreter registration order.
# - Resolve the first compatible interpreter for KnowledgeSourceInput.
# - Report whether compatible source interpretation is available.
# - Reject duplicate interpreter references.
# - Validate interpreter identity and version during registration.
#
# Must Not:
# - Interpret customer sources directly.
# - Acquire or inspect Knowledge content.
# - Contain source-technology-specific branching.
# - Select acquisition adapters, parsers, derivation, or representations.
# - Perform indexing, retrieval, Evidence construction, or evaluation.
# - Implement source-selection intelligence or execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Concrete deterministic implementation of the interpreter registry.
# - Composition mechanism for configured source interpreters.
# - Keeps source capability resolution behind a stable runtime boundary.
#
# Future Extensibility:
# - Additional source interpreters can register without runtime changes.
# - Profile and capability intelligence can evolve above this registry.
# - Plugin-backed registries can implement the stable interface separately.
# - More advanced selection policy can replace this implementation.

from __future__ import annotations

from alhf.rag.runtime.contracts.knowledge_source_input import (
    KnowledgeSourceInput,
)
from alhf.rag.runtime.interfaces.knowledge_source_interpreter import (
    KnowledgeSourceInterpreter,
)
from alhf.rag.runtime.interfaces.knowledge_source_interpreter_registry import (
    KnowledgeSourceInterpreterRegistry,
)


class InMemorySourceInterpreterRegistry(
    KnowledgeSourceInterpreterRegistry,
):
    """In-memory registry of configured Knowledge source interpreters."""

    def __init__(self) -> None:
        self._interpreters: dict[str, KnowledgeSourceInterpreter] = {}

    def register(
        self,
        interpreter: KnowledgeSourceInterpreter,
    ) -> None:
        """Register one configured Knowledge source interpreter."""

        if not isinstance(
            interpreter,
            KnowledgeSourceInterpreter,
        ):
            raise TypeError(
                "interpreter must be an instance of "
                "KnowledgeSourceInterpreter"
            )

        interpreter_ref = self._required_text(
            value=interpreter.interpreter_ref,
            field_name="interpreter_ref",
        )
        self._required_text(
            value=interpreter.interpreter_version,
            field_name="interpreter_version",
        )

        if interpreter_ref in self._interpreters:
            raise ValueError(
                f"interpreter already registered: {interpreter_ref}"
            )

        self._interpreters[interpreter_ref] = interpreter

    def resolve(
        self,
        source: KnowledgeSourceInput,
    ) -> KnowledgeSourceInterpreter:
        """Resolve the first compatible registered source interpreter."""

        self._validate_source(source)

        for interpreter in self._interpreters.values():
            if interpreter.supports(source):
                return interpreter

        raise LookupError(
            "source interpreter not found for Knowledge source input"
        )

    def contains(
        self,
        source: KnowledgeSourceInput,
    ) -> bool:
        """Return whether a compatible source interpreter is registered."""

        self._validate_source(source)

        return any(
            interpreter.supports(source)
            for interpreter in self._interpreters.values()
        )

    def __contains__(
        self,
        interpreter_ref: object,
    ) -> bool:
        """Return whether an interpreter reference is registered."""

        if not isinstance(
            interpreter_ref,
            str,
        ):
            return False

        normalized_ref = interpreter_ref.strip()

        if not normalized_ref:
            return False

        return normalized_ref in self._interpreters

    def __len__(self) -> int:
        """Return the number of registered source interpreters."""

        return len(self._interpreters)

    @staticmethod
    def _validate_source(
        source: KnowledgeSourceInput,
    ) -> None:
        """Validate source input supplied for capability resolution."""

        if not isinstance(
            source,
            KnowledgeSourceInput,
        ):
            raise TypeError(
                "source must be an instance of KnowledgeSourceInput"
            )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required registry text."""

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized
