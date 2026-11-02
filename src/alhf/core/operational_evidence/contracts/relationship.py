# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines universal relationship semantics used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# Operational evidence must preserve explicit relationships between
# records, executions, operations, and governed artifacts so downstream
# failure analysis can reconstruct execution and transformation history.
#
# A relationship recorded during execution must describe a known
# structural or dependency fact without being mistaken for a
# root-cause conclusion.
#
# Responsibilities:
# - Represent one immutable relationship between two references.
# - Preserve the semantic type of the relationship.
# - Preserve relationship direction.
# - Normalize and validate relationship references.
# - Prevent invalid self-referential relationships.
# - Provide storage-independent relationship semantics.
#
# Must Not:
# - Infer or assert diagnosed causality.
# - Perform root-cause analysis.
# - Perform failure analysis.
# - Contain RAG or Knowledge-specific semantics.
# - Contain workflow, task, or agent-specific semantics.
# - Define persistence, JSON, or JSONL behavior.
# - Contain provider-specific identifiers or storage locations.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Universal ALHF Operational Evidence contract.
# - Complements ExecutionIdentity without replacing its parent-operation
#   hierarchy.
# - Provides explicit cross-record and cross-artifact relationships for
#   future operational evidence records.
#
# Reuse Value:
# - Knowledge Foundation operational evidence.
# - Multi-agent operational evidence.
# - V3 operational evidence.
# - Failure analysis and RCA.
# - Corrective-action traceability.
# - Post-remediation validation.
#
# Future Extensibility:
# - Knowledge-specific references remain defined by Knowledge contracts.
# - Additional relationship types may be introduced when they represent
#   genuinely universal relationship semantics.
# - Analytical causal findings remain separate from observed
#   operational relationships.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RelationshipType(str, Enum):
    """Universal relationship types for ALHF operational evidence."""

    REFERENCES = "REFERENCES"
    DERIVED_FROM = "DERIVED_FROM"
    DEPENDS_ON = "DEPENDS_ON"
    BASED_ON = "BASED_ON"
    REMEDIATES = "REMEDIATES"
    VALIDATES = "VALIDATES"
    SUPERSEDES = "SUPERSEDES"
    RELATED_TO = "RELATED_TO"


@dataclass(frozen=True, slots=True)
class OperationalRelationship:
    """
    Immutable relationship between two governed references.

    source_ref:
        Identifier of the record, operation, execution, or governed
        artifact from which the relationship originates.

    target_ref:
        Identifier of the record, operation, execution, or governed
        artifact to which the relationship points.

    relationship_type:
        Describes the known semantic relationship between the source
        and target references.

    This contract represents explicit relationships only. A relationship
    such as DEPENDS_ON or DERIVED_FROM does not independently establish
    that the target caused a later failure.
    """

    source_ref: str
    target_ref: str
    relationship_type: RelationshipType

    def __post_init__(self) -> None:
        source_ref = self._normalize_reference(
            value=self.source_ref,
            field_name="source_ref",
        )
        target_ref = self._normalize_reference(
            value=self.target_ref,
            field_name="target_ref",
        )

        if not isinstance(
            self.relationship_type,
            RelationshipType,
        ):
            raise TypeError(
                "relationship_type must be an instance of "
                "RelationshipType"
            )

        if source_ref == target_ref:
            raise ValueError(
                "source_ref cannot equal target_ref"
            )

        object.__setattr__(
            self,
            "source_ref",
            source_ref,
        )
        object.__setattr__(
            self,
            "target_ref",
            target_ref,
        )

    @staticmethod
    def _normalize_reference(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize a required relationship reference."""

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
