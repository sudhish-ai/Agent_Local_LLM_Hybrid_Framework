# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the Knowledge-specific context attached to ALHF
# Operational Evidence.
#
# Problem Solved:
# Knowledge Foundation operations must connect universal Operational
# Evidence to governed Knowledge state without placing RAG-specific
# identities inside the universal evidence contracts.
#
# Responsibilities:
# - Preserve the applicable Knowledge scope reference.
# - Preserve optional logical resource and revision references.
# - Preserve optional derivation and Knowledge Unit references.
# - Preserve optional derived-artifact and affected-scope references.
# - Normalize and validate Knowledge evidence references.
# - Provide immutable Knowledge-specific evidence context.
#
# Must Not:
# - Duplicate Knowledge content.
# - Define Knowledge identity generation.
# - Define Knowledge lifecycle semantics.
# - Perform retrieval or indexing.
# - Perform failure analysis or root-cause analysis.
# - Infer causality.
# - Contain embedding vectors or retrieved content.
# - Contain persistence, JSON, or JSONL behavior.
# - Modify universal Operational Evidence contracts.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Knowledge-specific extension for ALHF Operational Evidence.
# - Lives outside the universal Operational Evidence core.
# - References governed Knowledge state rather than duplicating it.
#
# Reuse Value:
# - Standard RAG operational evidence.
# - GraphRAG operational evidence.
# - Agentic RAG operational evidence.
# - Knowledge failure analysis and RCA.
# - Affected-scope analysis.
# - Corrective-action and validation workflows.
#
# Future Extensibility:
# - Additional Knowledge artifact references can evolve independently
#   from universal Operational Evidence.
# - Graph-specific and Agentic-RAG-specific semantics remain outside
#   this common Knowledge context unless universally required.
# - Knowledge identity contracts remain authoritative for referenced
#   Knowledge state.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KnowledgeEvidenceContext:
    """
    Immutable Knowledge-specific context for Operational Evidence.

    knowledge_scope_ref:
        Governed reference identifying the applicable Knowledge scope.

    logical_resource_ref:
        Optional governed reference to a logical Knowledge resource.

    revision_ref:
        Optional governed reference to an exact resource revision.

    derivation_ref:
        Optional governed reference to a Knowledge derivation.

    knowledge_unit_ref:
        Optional governed reference to a Knowledge Unit.

    derived_artifact_ref:
        Optional governed reference to a derived Knowledge artifact.

    affected_scope_ref:
        Optional governed reference identifying the scope affected by
        an operational condition without embedding large identifier sets.
    """

    knowledge_scope_ref: str
    logical_resource_ref: str | None = None
    revision_ref: str | None = None
    derivation_ref: str | None = None
    knowledge_unit_ref: str | None = None
    derived_artifact_ref: str | None = None
    affected_scope_ref: str | None = None

    def __post_init__(self) -> None:
        knowledge_scope_ref = self._normalize_required_reference(
            value=self.knowledge_scope_ref,
            field_name="knowledge_scope_ref",
        )

        optional_references = {
            "logical_resource_ref": self.logical_resource_ref,
            "revision_ref": self.revision_ref,
            "derivation_ref": self.derivation_ref,
            "knowledge_unit_ref": self.knowledge_unit_ref,
            "derived_artifact_ref": self.derived_artifact_ref,
            "affected_scope_ref": self.affected_scope_ref,
        }

        normalized_references = {
            field_name: self._normalize_optional_reference(
                value=value,
                field_name=field_name,
            )
            for field_name, value in optional_references.items()
        }

        object.__setattr__(
            self,
            "knowledge_scope_ref",
            knowledge_scope_ref,
        )

        for field_name, value in normalized_references.items():
            object.__setattr__(
                self,
                field_name,
                value,
            )

    @staticmethod
    def _normalize_required_reference(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize a required Knowledge reference."""

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized_value

    @staticmethod
    def _normalize_optional_reference(
        *,
        value: str | None,
        field_name: str,
    ) -> str | None:
        """Validate and normalize an optional Knowledge reference."""

        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string or None"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} cannot be empty when provided"
            )

        return normalized_value
