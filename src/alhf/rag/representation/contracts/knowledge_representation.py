# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the provider-neutral retrieval representation produced from
# one ALHF Knowledge Unit.
#
# Problem Solved:
# Knowledge Units must remain independent from embedding models, vector
# stores, sparse indexes, graph systems, and future retrieval technology.
# This contract separates governed Knowledge truth from retrieval-
# optimized representations.
#
# Responsibilities:
# - Identify one representation of a Knowledge Unit.
# - Preserve Knowledge Unit and source provenance.
# - Declare the universal representation kind.
# - Preserve representation payload without provider coupling.
# - Preserve representation strategy identity and version.
# - Preserve representation model identity where applicable.
# - Support multiple representations for one Knowledge Unit.
# - Provide immutable representation semantics.
#
# Must Not:
# - Modify Knowledge Unit content or identity.
# - Perform embedding or representation generation.
# - Contain vector-store-specific records or identifiers.
# - Contain LangChain, LangGraph, or external framework types.
# - Perform indexing, retrieval, reranking, or context construction.
# - Assume one representation per Knowledge Unit.
# - Assume dense vectors are the only retrieval representation.
# - Implement concurrency or NFT execution policy.
#
# Architectural Position:
# - Stable boundary between Knowledge Units and retrieval technology.
# - Allows representation providers and models to evolve independently.
# - Prevents embedding or index technology from contaminating Knowledge.
#
# Reuse Value:
# - Dense vector representations.
# - Sparse representations.
# - Lexical representations.
# - Structured representations.
# - Graph-oriented representations.
# - Future multimodal and hybrid retrieval foundations.
#
# Future Extensibility:
# - Multiple representation versions may coexist during migration.
# - Provider/model changes require new representations, not re-derivation.
# - Hybrid retrieval can combine independently governed representations.
# - External tools can implement representation providers behind ALHF
#   boundaries without changing this contract.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RepresentationKind(str, Enum):
    """Universal categories of retrieval representation."""

    DENSE = "DENSE"
    SPARSE = "SPARSE"
    LEXICAL = "LEXICAL"
    STRUCTURED = "STRUCTURED"
    GRAPH = "GRAPH"
    MULTIMODAL = "MULTIMODAL"


@dataclass(frozen=True, slots=True)
class KnowledgeRepresentation:
    """Immutable retrieval representation of one Knowledge Unit."""

    representation_id: str
    knowledge_unit_ref: str
    derivation_id: str
    knowledge_scope_ref: str
    resource_ref: str
    revision_ref: str
    kind: RepresentationKind
    payload: bytes
    media_type: str
    strategy_ref: str
    strategy_version: str
    model_ref: str | None = None
    model_version: str | None = None

    def __post_init__(self) -> None:
        required_fields = (
            "representation_id",
            "knowledge_unit_ref",
            "derivation_id",
            "knowledge_scope_ref",
            "resource_ref",
            "revision_ref",
            "media_type",
            "strategy_ref",
            "strategy_version",
        )

        for field_name in required_fields:
            normalized = self._required_text(
                value=getattr(self, field_name),
                field_name=field_name,
            )
            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        if not isinstance(
            self.kind,
            RepresentationKind,
        ):
            raise TypeError(
                "kind must be an instance of RepresentationKind"
            )

        if not isinstance(
            self.payload,
            bytes,
        ):
            raise TypeError(
                "payload must be bytes"
            )

        self._validate_optional_model_fields()

    @property
    def size_bytes(self) -> int:
        """Return representation payload size without copying it."""

        return len(self.payload)

    def _validate_optional_model_fields(self) -> None:
        if (
            self.model_ref is None
            and self.model_version is None
        ):
            return

        if (
            self.model_ref is None
            or self.model_version is None
        ):
            raise ValueError(
                "model_ref and model_version must be provided together"
            )

        model_ref = self._required_text(
            value=self.model_ref,
            field_name="model_ref",
        )
        model_version = self._required_text(
            value=self.model_version,
            field_name="model_version",
        )

        object.__setattr__(
            self,
            "model_ref",
            model_ref,
        )
        object.__setattr__(
            self,
            "model_version",
            model_version,
        )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required contract text."""

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
