# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the ALHF Knowledge Foundation V1 real-PDF E2E path.
#
# Responsibilities:
# - Create a real text-bearing PDF on disk.
# - Acquire it through LocalFileAdapter and AcquisitionService.
# - Parse and normalize it through the ingestion boundary.
# - Derive Knowledge Units from canonical content.
# - Produce lexical Knowledge representations.
# - Index representations through IndexingService.
# - Execute a consumer-facing KnowledgeRequest.
# - Construct Evidence and bounded KnowledgeContext.
# - Evaluate the resulting Context.
# - Validate end-to-end provenance and no-match behavior.
#
# Must Not:
# - Mock Knowledge Foundation stages.
# - Introduce PDF-specific downstream behavior.
# - Invoke an LLM or assemble a model prompt.
# - Test semantic retrieval, reranking, or advanced intelligence.

from io import BytesIO

from reportlab.pdfgen import canvas

from alhf.rag.chunking.derivation_service import DerivationService
from alhf.rag.chunking.providers.in_memory_derivation_registry import (
    InMemoryDerivationRegistry,
)
from alhf.rag.chunking.strategies.fixed_size_text_derivation import (
    FixedSizeTextDerivation,
)
from alhf.rag.context_packing.context_packing_service import (
    ContextPackingService,
)
from alhf.rag.context_packing.providers.deterministic_context_packer import (
    DeterministicContextPacker,
)
from alhf.rag.evaluation.contracts.evaluation_result import (
    EvaluationStatus,
)
from alhf.rag.evaluation.evaluation_service import EvaluationService
from alhf.rag.evaluation.providers.deterministic_context_evaluator import (
    DeterministicContextEvaluator,
)
from alhf.rag.evidence.evidence_service import EvidenceService
from alhf.rag.evidence.providers.candidate_evidence_builder import (
    CandidateEvidenceBuilder,
)
from alhf.rag.indexing.indexing_service import IndexingService
from alhf.rag.indexing.providers.in_memory_index_provider import (
    InMemoryIndexProvider,
)
from alhf.rag.indexing.providers.in_memory_index_registry import (
    InMemoryIndexRegistry,
)
from alhf.rag.ingestion.acquisition_service import DefaultAcquisitionService
from alhf.rag.ingestion.contracts.acquisition_request import (
    AcquisitionRequest,
)
from alhf.rag.ingestion.contracts.adapter_capabilities import (
    AdapterCapabilities,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)
from alhf.rag.ingestion.normalization_service import NormalizationService
from alhf.rag.ingestion.normalizers.text_content_normalizer import (
    TextContentNormalizer,
)
from alhf.rag.ingestion.parsers.pdf_resource_parser import PdfResourceParser
from alhf.rag.ingestion.providers.in_memory_adapter_registry import (
    InMemoryAdapterRegistry,
)
from alhf.rag.ingestion.providers.in_memory_normalizer_registry import (
    InMemoryNormalizerRegistry,
)
from alhf.rag.ingestion.providers.local_file_adapter import LocalFileAdapter
from alhf.rag.knowledge_request.contracts.knowledge_request import (
    KnowledgeRequest,
)
from alhf.rag.knowledge_request.knowledge_query_service import (
    KnowledgeQueryService,
)
from alhf.rag.representation.providers.deterministic_text_representation_provider import (
    DeterministicTextRepresentationProvider,
)
from alhf.rag.representation.providers.in_memory_representation_registry import (
    InMemoryRepresentationRegistry,
)
from alhf.rag.representation.representation_service import (
    RepresentationService,
)
from alhf.rag.retrieval.providers.in_memory_lexical_retriever import (
    InMemoryLexicalRetriever,
)
from alhf.rag.retrieval.retrieval_service import RetrievalService


def _write_pdf(path) -> None:
    stream = BytesIO()
    pdf = canvas.Canvas(stream)

    pdf.drawString(
        72,
        720,
        "Enterprise authentication policy requires MFA.",
    )
    pdf.drawString(
        72,
        700,
        "Privileged access requires additional approval.",
    )
    pdf.save()

    path.write_bytes(
        stream.getvalue()
    )


def _ingest(tmp_path):
    _write_pdf(
        tmp_path / "policy.pdf"
    )

    adapter = LocalFileAdapter(
        root_directory=tmp_path,
        max_resource_bytes=1_000_000,
    )

    adapters = InMemoryAdapterRegistry()
    adapters.register(
        adapter_ref="local-file",
        adapter=adapter,
        capabilities=AdapterCapabilities(),
    )

    source = KnowledgeSource(
        source_id="policy-source",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="local-file",
    )

    session = DefaultAcquisitionService(
        registry=adapters,
    ).acquire(
        AcquisitionRequest(
            source=source,
            max_resources=1,
        )
    )

    resource = next(
        session.resources()
    )

    parsed = PdfResourceParser().parse(
        resource
    )

    normalizers = InMemoryNormalizerRegistry()
    normalizers.register(
        TextContentNormalizer()
    )

    canonical = NormalizationService(
        registry=normalizers,
    ).normalize(
        parsed
    )

    derivations = InMemoryDerivationRegistry()
    derivations.register(
        FixedSizeTextDerivation(
            chunk_size_bytes=4096,
        )
    )

    units = DerivationService(
        registry=derivations,
    ).derive(
        canonical
    )

    representations = InMemoryRepresentationRegistry()
    representations.register(
        DeterministicTextRepresentationProvider()
    )

    service = RepresentationService(
        registry=representations,
    )

    return resource, (
        service.represent(unit)
        for unit in units
    )


def _runtime(tmp_path):
    resource, representations = _ingest(
        tmp_path
    )

    provider = InMemoryIndexProvider()

    indexes = InMemoryIndexRegistry()
    indexes.register(
        index_ref="knowledge-index",
        provider=provider,
    )

    indexing = IndexingService(
        registry=indexes,
    )

    for representation in representations:
        indexing.index(
            index_ref="knowledge-index",
            representation=representation,
        )

    query = KnowledgeQueryService(
        retrieval_service=RetrievalService(
            retriever=InMemoryLexicalRetriever(
                provider=provider,
            )
        ),
        evidence_service=EvidenceService(
            builder=CandidateEvidenceBuilder(),
            resolve_representation=provider.get,
        ),
        context_packing_service=ContextPackingService(
            packer=DeterministicContextPacker(),
        ),
        evaluation_service=EvaluationService(
            evaluator=DeterministicContextEvaluator(),
        ),
    )

    return resource, provider, query


def _request(
    text: str,
) -> KnowledgeRequest:
    return KnowledgeRequest(
        request_id="request-001",
        knowledge_scope_ref="scope-001",
        query=text,
        index_ref="knowledge-index",
        index_version="v1",
        retrieval_limit=5,
        max_context_bytes=4096,
    )


def test_real_pdf_reaches_evaluated_knowledge_context(
    tmp_path,
) -> None:
    resource, provider, query = _runtime(
        tmp_path
    )

    context, evaluation = query.execute(
        request=_request(
            "authentication MFA"
        )
    )

    assert len(provider) == 1
    assert (
        b"authentication policy requires MFA"
        in context.content
    )
    assert context.evidence_count == 1
    assert evaluation.subject_ref == context.context_id
    assert evaluation.status == EvaluationStatus.PASS

    representation = next(
        provider.representations()
    )

    assert representation.resource_ref == resource.resource_ref
    assert representation.revision_ref == resource.revision_ref
    assert representation.knowledge_scope_ref == "scope-001"


def test_pdf_query_preserves_end_to_end_lineage(
    tmp_path,
) -> None:
    resource, provider, query = _runtime(
        tmp_path
    )

    representation = next(
        provider.representations()
    )

    context, _ = query.execute(
        request=_request(
            "privileged approval"
        )
    )

    assert representation.representation_id.startswith(
        "representation:"
    )
    assert representation.knowledge_unit_ref.startswith(
        "unit:"
    )
    assert representation.derivation_id.startswith(
        "derivation:"
    )
    assert representation.resource_ref == resource.resource_ref

    assert len(context.evidence_refs) == 1
    assert (
        b"Privileged access requires additional approval"
        in context.content
    )


def test_absent_pdf_knowledge_is_inconclusive(
    tmp_path,
) -> None:
    _, _, query = _runtime(
        tmp_path
    )

    context, evaluation = query.execute(
        request=_request(
            "quantum computing"
        )
    )

    assert context.content == b""
    assert context.evidence_refs == ()
    assert evaluation.status == EvaluationStatus.INCONCLUSIVE
    assert evaluation.score == 0.0


def test_real_pdf_e2e_is_deterministic(
    tmp_path,
) -> None:
    _, _, query = _runtime(
        tmp_path
    )

    request = _request(
        "authentication MFA"
    )

    first = query.execute(
        request=request
    )
    second = query.execute(
        request=request
    )

    assert first == second
