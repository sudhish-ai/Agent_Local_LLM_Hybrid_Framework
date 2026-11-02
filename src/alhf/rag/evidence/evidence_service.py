# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides provider-neutral Evidence orchestration for ALHF RAG V1.
#
# Problem Solved:
# Retrieval results reference Knowledge representations but do not own
# their content. Evidence construction requires controlled resolution of
# that representation before producing governed Evidence artifacts.
#
# Responsibilities:
# - Accept one RetrievalResult.
# - Resolve its originating KnowledgeRepresentation.
# - Delegate Evidence construction to EvidenceBuilder.
# - Validate Evidence output and provenance continuity.
# - Support incremental Evidence construction for result streams.
# - Fail explicitly when representation content cannot be resolved.
#
# Must Not:
# - Perform retrieval or reranking.
# - Implement representation storage.
# - Determine Evidence sufficiency.
# - Resolve Evidence conflicts.
# - Construct model Context or generate answers.
# - Implement Evidence Intelligence or verification.
# - Depend on external RAG frameworks.
#
# Architectural Position:
# - Orchestration boundary between Retrieval and governed Evidence.
# - Connects retrieval references to representation content.
# - Protects provenance before downstream Evidence consumption.
#
# Reuse Value:
# - V1 Standard RAG Evidence construction.
# - Local-first deterministic execution.
# - Evidence lineage and production RCA.
# - Future verified Evidence builders.
#
# Future Extensibility:
# - Durable representation repositories can replace local resolution.
# - Evidence verification can evolve behind EvidenceBuilder.
# - Sufficiency and conflict analysis remain downstream concerns.
# - GraphRAG and Agentic RAG can reuse this orchestration boundary.

from __future__ import annotations

from collections.abc import Iterator
from typing import Callable

from alhf.rag.evidence.contracts.evidence_item import (
    EvidenceItem,
)
from alhf.rag.evidence.interfaces.evidence_builder import (
    EvidenceBuilder,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)
from alhf.rag.retrieval.contracts.retrieval_result import (
    RetrievalResult,
)


class EvidenceService:
    """Orchestrate deterministic Evidence construction."""

    def __init__(
        self,
        *,
        builder: EvidenceBuilder,
        resolve_representation: Callable,
    ) -> None:
        if not isinstance(
            builder,
            EvidenceBuilder,
        ):
            raise TypeError(
                "builder must be an instance of EvidenceBuilder"
            )

        if not callable(
            resolve_representation
        ):
            raise TypeError(
                "resolve_representation must be callable"
            )

        self._builder = builder
        self._resolve_representation = resolve_representation

    def build(
        self,
        *,
        result: RetrievalResult,
    ) -> EvidenceItem:
        """Construct Evidence for one retrieval candidate."""

        self._validate_result(
            result
        )

        representation = self._resolve(
            result.representation_ref
        )

        item = self._builder.build(
            result=result,
            representation=representation,
        )

        if not isinstance(
            item,
            EvidenceItem,
        ):
            raise TypeError(
                "builder must return EvidenceItem"
            )

        self._validate_item(
            result=result,
            item=item,
        )

        return item

    def build_many(
        self,
        *,
        results: Iterator,
    ):
        """Yield Evidence incrementally for retrieval results."""

        if not isinstance(
            results,
            Iterator,
        ):
            raise TypeError(
                "results must be an Iterator"
            )

        for result in results:
            yield self.build(
                result=result
            )

    def _resolve(
        self,
        representation_ref: str,
    ) -> KnowledgeRepresentation:
        representation = self._resolve_representation(
            representation_ref
        )

        if representation is None:
            raise LookupError(
                f"representation not found: {representation_ref}"
            )

        if not isinstance(
            representation,
            KnowledgeRepresentation,
        ):
            raise TypeError(
                "resolver must return "
                "KnowledgeRepresentation or None"
            )

        return representation

    @staticmethod
    def _validate_result(
        result: RetrievalResult,
    ) -> None:
        if not isinstance(
            result,
            RetrievalResult,
        ):
            raise TypeError(
                "result must be an instance of RetrievalResult"
            )

    @staticmethod
    def _validate_item(
        *,
        result: RetrievalResult,
        item: EvidenceItem,
    ) -> None:
        checks = (
            (
                item.representation_ref,
                result.representation_ref,
                "representation_ref",
            ),
            (
                item.knowledge_unit_ref,
                result.knowledge_unit_ref,
                "knowledge_unit_ref",
            ),
            (
                item.derivation_id,
                result.derivation_id,
                "derivation_id",
            ),
            (
                item.knowledge_scope_ref,
                result.knowledge_scope_ref,
                "knowledge_scope_ref",
            ),
            (
                item.resource_ref,
                result.resource_ref,
                "resource_ref",
            ),
            (
                item.revision_ref,
                result.revision_ref,
                "revision_ref",
            ),
        )

        for actual, expected, field_name in checks:
            if actual != expected:
                raise ValueError(
                    f"Evidence {field_name} must match RetrievalResult"
                )
