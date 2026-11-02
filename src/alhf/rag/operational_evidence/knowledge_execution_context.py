# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the reusable execution context used when Knowledge Foundation
# stages emit Operational Evidence.
#
# Responsibilities:
# - Preserve universal execution identity for a Knowledge operation.
# - Preserve governed Knowledge-specific evidence context.
# - Keep execution identity stable across related Knowledge events.
# - Provide immutable context for Knowledge Operational Evidence services.
# - Simplify stage integration without duplicating evidence semantics.
#
# Must Not:
# - Generate execution, operation, or Knowledge identities.
# - Create Operational Evidence records.
# - Persist Operational Evidence.
# - Perform JSON or JSONL serialization.
# - Execute acquisition, parsing, retrieval, or indexing.
# - Perform failure analysis or root-cause analysis.
# - Infer causality.
# - Contain Knowledge content, prompts, embeddings, or retrieved text.
# - Contain provider-specific behavior.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Knowledge-specific Operational Evidence execution context.
# - Composes universal ExecutionIdentity with KnowledgeEvidenceContext.
# - Used by Knowledge stages when emitting multiple related events.
#
# Future Extensibility:
# - Stage-specific operational facts remain separate from this context.
# - Additional governed Knowledge references evolve through
#   KnowledgeEvidenceContext.
# - Universal execution semantics remain owned by ExecutionIdentity.

from __future__ import annotations

from dataclasses import dataclass

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.rag.operational_evidence.contracts.knowledge_evidence_context import (
    KnowledgeEvidenceContext,
)


@dataclass(frozen=True, slots=True)
class KnowledgeExecutionContext:
    """
    Immutable execution context for Knowledge Operational Evidence.

    execution:
        Universal identity of the execution and operation emitting
        Knowledge Operational Evidence.

    knowledge:
        Governed Knowledge-specific context associated with the
        execution.

    This contract carries stable execution context only. Event type,
    operational outcome, measurements, relationships, persistence, and
    analytical conclusions remain separate responsibilities.
    """

    execution: ExecutionIdentity
    knowledge: KnowledgeEvidenceContext

    def __post_init__(self) -> None:
        self._validate_contract(
            value=self.execution,
            expected_type=ExecutionIdentity,
            field_name="execution",
        )
        self._validate_contract(
            value=self.knowledge,
            expected_type=KnowledgeEvidenceContext,
            field_name="knowledge",
        )

    @property
    def correlation_id(self) -> str:
        """Return the broader ALHF correlation identity."""

        return self.execution.correlation_id

    @property
    def execution_id(self) -> str:
        """Return the concrete ALHF execution identity."""

        return self.execution.execution_id

    @property
    def operation_id(self) -> str:
        """Return the concrete operation identity."""

        return self.execution.operation_id

    @property
    def parent_operation_id(self) -> str | None:
        """Return the immediate parent operation identity."""

        return self.execution.parent_operation_id

    @property
    def knowledge_scope_ref(self) -> str:
        """Return the governed Knowledge scope reference."""

        return self.knowledge.knowledge_scope_ref

    @staticmethod
    def _validate_contract(
        *,
        value: object,
        expected_type: type,
        field_name: str,
    ) -> None:
        """Validate one required composed contract."""

        if not isinstance(
            value,
            expected_type,
        ):
            raise TypeError(
                f"{field_name} must be an instance of "
                f"{expected_type.__name__}"
            )
