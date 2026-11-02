# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the deterministic fixed-size text derivation strategy used by
# the ALHF Knowledge Foundation V1 chunking layer.
#
# Problem Solved:
# V1 requires a simple, reproducible derivation mechanism for converting
# canonical text into bounded Knowledge Units while preserving stable
# identity, provenance, and downstream strategy independence.
#
# Responsibilities:
# - Accept canonical TEXT content.
# - Derive bounded text Knowledge Units incrementally.
# - Support explicit configurable chunk size and overlap.
# - Preserve ResourceIdentity and canonical provenance.
# - Generate deterministic derivation and Knowledge Unit identities.
# - Preserve deterministic unit ordering.
# - Expose strategy identity and version for reproducibility.
#
# Must Not:
# - Acquire, parse, or normalize Knowledge content.
# - Contain source-specific or file-format-specific behavior.
# - Select chunk size or overlap intelligently.
# - Implement North-Star Derivation Intelligence.
# - Generate embeddings or retrieval representations.
# - Perform indexing, retrieval, reranking, or context construction.
# - Materialize an unbounded Knowledge Unit collection.
# - Implement concurrency or NFT execution policy.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Concrete V1 implementation of DerivationStrategy.
# - Deterministic baseline behind the universal derivation boundary.
# - Produces provider-neutral KnowledgeUnit contracts.
#
# Reuse Value:
# - V1 Standard RAG implementation.
# - Deterministic derivation testing.
# - Baseline retrieval-quality evaluation.
# - Future comparison against semantic and adaptive strategies.
#
# Future Extensibility:
# - Evidence-driven intelligence can replace strategy selection later.
# - Semantic, hierarchical, and structure-aware strategies can coexist.
# - Retrieval evaluation can compare this baseline with new strategies.
# - External framework strategies can implement the same ALHF boundary
#   without changing KnowledgeUnit consumers.

from __future__ import annotations

import hashlib

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.chunking.interfaces.derivation_strategy import (
    DerivationStrategy,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
    CanonicalContentKind,
)


class FixedSizeTextDerivation(DerivationStrategy):
    """Derive deterministic bounded units from canonical UTF-8 text."""

    _STRATEGY_REF = "fixed-size-text-derivation"
    _STRATEGY_VERSION = "1.0"

    def __init__(
        self,
        *,
        chunk_size_bytes: int,
        overlap_bytes: int = 0,
    ) -> None:
        self._chunk_size_bytes = self._positive_int(
            value=chunk_size_bytes,
            field_name="chunk_size_bytes",
        )
        self._overlap_bytes = self._non_negative_int(
            value=overlap_bytes,
            field_name="overlap_bytes",
        )

        if self._overlap_bytes >= self._chunk_size_bytes:
            raise ValueError(
                "overlap_bytes must be smaller than chunk_size_bytes"
            )

    @property
    def strategy_ref(self) -> str:
        """Return the stable strategy identifier."""

        return self._STRATEGY_REF

    @property
    def strategy_version(self) -> str:
        """Return the stable strategy behavior version."""

        return self._STRATEGY_VERSION

    def supports(
        self,
        content: CanonicalContent,
    ) -> bool:
        """Return whether canonical content has TEXT semantics."""

        return (
            isinstance(content, CanonicalContent)
            and content.content_kind == CanonicalContentKind.TEXT
            and content.media_type.strip().lower() == "text/plain"
        )

    def derive(
        self,
        content: CanonicalContent,
    ):
        """Yield deterministic bounded Knowledge Units incrementally."""

        if not isinstance(content, CanonicalContent):
            raise TypeError(
                "content must be an instance of CanonicalContent"
            )

        if not self.supports(content):
            raise ValueError(
                "FixedSizeTextDerivation requires canonical text content"
            )

        if not content.content:
            return

        derivation_id = self._derivation_id(content)
        canonical_ref = self._canonical_ref(content)
        step = self._chunk_size_bytes - self._overlap_bytes
        sequence = 0
        start = 0

        while start < len(content.content):
            end = min(
                start + self._chunk_size_bytes,
                len(content.content),
            )
            unit_content = content.content[start:end]

            yield KnowledgeUnit(
                unit_id=self._unit_id(
                    derivation_id=derivation_id,
                    sequence=sequence,
                    content=unit_content,
                ),
                identity=content.identity,
                canonical_artifact_ref=canonical_ref,
                derivation_id=derivation_id,
                sequence=sequence,
                content=unit_content,
                content_kind=content.content_kind,
                media_type=content.media_type,
                strategy_ref=self.strategy_ref,
                strategy_version=self.strategy_version,
            )

            sequence += 1
            start += step

    def _derivation_id(
        self,
        content: CanonicalContent,
    ) -> str:
        material = (
            f"{content.knowledge_scope_ref}|"
            f"{content.resource_ref}|"
            f"{content.revision_ref}|"
            f"{self.strategy_ref}|"
            f"{self.strategy_version}|"
            f"{self._chunk_size_bytes}|"
            f"{self._overlap_bytes}"
        ).encode("utf-8")

        return "derivation:" + hashlib.sha256(material).hexdigest()

    @staticmethod
    def _canonical_ref(
        content: CanonicalContent,
    ) -> str:
        material = (
            content.identity.knowledge_scope_ref
            + "|"
            + content.resource_ref
            + "|"
            + content.revision_ref
            + "|"
            + content.normalizer_ref
            + "|"
            + content.normalizer_version
        ).encode("utf-8")

        return "canonical:" + hashlib.sha256(material).hexdigest()

    @staticmethod
    def _unit_id(
        *,
        derivation_id: str,
        sequence: int,
        content: bytes,
    ) -> str:
        digest = hashlib.sha256(
            derivation_id.encode("utf-8")
            + b"|"
            + str(sequence).encode("ascii")
            + b"|"
            + content
        ).hexdigest()

        return "unit:" + digest

    @staticmethod
    def _positive_int(
        *,
        value: int,
        field_name: str,
    ) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                f"{field_name} must be an int"
            )

        if value <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero"
            )

        return value

    @staticmethod
    def _non_negative_int(
        *,
        value: int,
        field_name: str,
    ) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                f"{field_name} must be an int"
            )

        if value < 0:
            raise ValueError(
                f"{field_name} cannot be negative"
            )

        return value
