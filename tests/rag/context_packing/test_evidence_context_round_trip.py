# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the ALHF V1 Retrieval-to-Evidence-to-Context round trip.
#
# Responsibilities:
# - Retrieve indexed lexical Knowledge.
# - Construct governed candidate Evidence.
# - Pack Evidence into bounded KnowledgeContext.
# - Preserve Knowledge and Evidence lineage.
# - Preserve retrieval-ranked Evidence ordering.
# - Validate bounded Context behavior.
# - Validate deterministic Context construction.
#
# Must Not:
# - Test semantic retrieval or embeddings.
# - Treat candidate Evidence as verified support.
# - Determine Evidence sufficiency.
# - Generate prompts or answers.
# - Test token budgeting or model routing.
# - Test adaptive Context Intelligence.
# - Depend on external RAG frameworks.

from alhf.rag.context_packing.context_packing_service import (
    ContextPackingService,
)
from alhf.rag.context_packing.contracts.knowledge_context import (
    KnowledgeContext,
)
from alhf.rag.context_packing.providers.deterministic_context_packer import (
    DeterministicContextPacker,
)
from alhf.rag.evidence.evidence_service import (
    EvidenceService,
)
from alhf.rag.evidence.providers.candidate_evidence_builder import (
    CandidateEvidenceBuilder,
)
from alhf.rag.indexing.providers.in_memory_index_provider import (
    InMemoryIndexProvider,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)
from alhf.rag.retrieval.providers.in_memory_lexical_retriever import (
    InMemoryLexicalRetriever,
)
from alhf.rag.retrieval.retrieval_service import (
    RetrievalService,
)


def _representation(
    representation_id: str,
    unit_ref: str,
    payload: bytes,
) -> KnowledgeRepresentation:
    return KnowledgeRepresentation(
        representation_id=representation_id,
        knowledge_unit_ref=unit_ref,
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
        kind=RepresentationKind.LEXICAL,
        payload=payload,
        media_type="text/plain",
        strategy_ref="deterministic-text-representation",
        strategy_version="1.0",
    )


def _pipeline():
    provider = InMemoryIndexProvider()

    provider.upsert(
        _representation(
            "representation-001",
            "unit-001",
            b"enterprise authentication policy",
        )
    )
    provider.upsert(
        _representation(
            "representation-002",
            "unit-002",
            b"enterprise travel policy",
        )
    )

    retrieval = RetrievalService(
        retriever=InMemoryLexicalRetriever(
            provider=provider,
        )
    )

    evidence = EvidenceService(
        builder=CandidateEvidenceBuilder(),
        resolve_representation=provider.get,
    )

    packing = ContextPackingService(
        packer=DeterministicContextPacker(),
    )

    return retrieval, evidence, packing


def _build_context(
    *,
    query: str,
    max_bytes: int = 1000,
) -> KnowledgeContext:
    retrieval, evidence, packing = _pipeline()

    results = retrieval.retrieve(
        query=query,
        index_ref="knowledge-index",
        index_version="v1",
        limit=5,
    )

    items = evidence.build_many(
        results=results,
    )

    return packing.pack(
        evidence=items,
        knowledge_scope_ref="scope-001",
        max_bytes=max_bytes,
    )


def test_retrieved_knowledge_reaches_context() -> None:
    context = _build_context(
        query="authentication",
    )

    assert isinstance(
        context,
        KnowledgeContext,
    )
    assert context.content == (
        b"enterprise authentication policy"
    )
    assert context.evidence_count == 1


def test_context_preserves_knowledge_scope() -> None:
    context = _build_context(
        query="authentication",
    )

    assert context.knowledge_scope_ref == "scope-001"


def test_context_preserves_evidence_lineage() -> None:
    retrieval, evidence, packing = _pipeline()

    result = next(
        retrieval.retrieve(
            query="authentication",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    item = evidence.build(
        result=result,
    )

    context = packing.pack(
        evidence=iter((item,)),
        knowledge_scope_ref="scope-001",
        max_bytes=1000,
    )

    assert context.evidence_refs == (
        item.evidence_id,
    )


def test_ranked_evidence_order_reaches_context() -> None:
    context = _build_context(
        query="enterprise policy",
    )

    assert context.content == (
        b"enterprise authentication policy"
        b"\n\n"
        b"enterprise travel policy"
    )
    assert context.evidence_count == 2


def test_context_boundary_excludes_later_evidence() -> None:
    first_content = b"enterprise authentication policy"

    context = _build_context(
        query="enterprise policy",
        max_bytes=len(first_content),
    )

    assert context.content == first_content
    assert context.evidence_count == 1


def test_no_retrieval_match_produces_empty_context() -> None:
    context = _build_context(
        query="nonexistent",
    )

    assert context.content == b""
    assert context.evidence_refs == ()
    assert context.evidence_count == 0


def test_round_trip_is_deterministic() -> None:
    first = _build_context(
        query="enterprise policy",
    )
    second = _build_context(
        query="enterprise policy",
    )

    assert first == second
    assert first.context_id == second.context_id
