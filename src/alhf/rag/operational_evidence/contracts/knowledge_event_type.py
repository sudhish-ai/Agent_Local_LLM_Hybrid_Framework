# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines Knowledge-specific Operational Evidence event semantics
# used by the ALHF Knowledge Foundation.
#
# Responsibilities:
# - Standardize significant Knowledge Foundation event names.
# - Preserve stage-specific operational semantics outside ALHF core.
# - Support acquisition and parsing evidence.
# - Support normalization and derivation evidence.
# - Support representation and indexing evidence.
# - Support retrieval and Evidence construction evidence.
# - Support context construction and evaluation evidence.
# - Provide stable string-compatible event values.
#
# Must Not:
# - Define universal ALHF event semantics.
# - Modify existing ALHF EventType enums.
# - Contain event-processing logic.
# - Contain persistence or serialization logic.
# - Perform failure analysis or root-cause analysis.
# - Define provider-specific implementation events.
# - Define GraphRAG-only or Agentic-RAG-only semantics.
#
# Architectural Position:
# - Knowledge-specific Operational Evidence contract.
# - Independent from universal ALHF event-type contracts.
# - Used with the universal OperationalEvidenceRecord event_name field.
#
# Future Extensibility:
# - New event types may be added when implementation evidence proves
#   they represent significant Knowledge Foundation operations.
# - GraphRAG and Agentic RAG may extend their own event vocabularies
#   without changing universal ALHF core semantics.

from __future__ import annotations

from enum import Enum


class KnowledgeEventType(str, Enum):
    """Knowledge Foundation Operational Evidence event types."""

    ACQUISITION_STARTED = "ACQUISITION_STARTED"
    ACQUISITION_COMPLETED = "ACQUISITION_COMPLETED"
    ACQUISITION_DEGRADED = "ACQUISITION_DEGRADED"
    ACQUISITION_FAILED = "ACQUISITION_FAILED"

    PARSING_STARTED = "PARSING_STARTED"
    PARSING_COMPLETED = "PARSING_COMPLETED"
    PARSING_DEGRADED = "PARSING_DEGRADED"
    PARSING_FAILED = "PARSING_FAILED"

    NORMALIZATION_STARTED = "NORMALIZATION_STARTED"
    NORMALIZATION_COMPLETED = "NORMALIZATION_COMPLETED"
    NORMALIZATION_DEGRADED = "NORMALIZATION_DEGRADED"
    NORMALIZATION_FAILED = "NORMALIZATION_FAILED"

    DERIVATION_STARTED = "DERIVATION_STARTED"
    DERIVATION_COMPLETED = "DERIVATION_COMPLETED"
    DERIVATION_DEGRADED = "DERIVATION_DEGRADED"
    DERIVATION_FAILED = "DERIVATION_FAILED"

    REPRESENTATION_STARTED = "REPRESENTATION_STARTED"
    REPRESENTATION_COMPLETED = "REPRESENTATION_COMPLETED"
    REPRESENTATION_DEGRADED = "REPRESENTATION_DEGRADED"
    REPRESENTATION_FAILED = "REPRESENTATION_FAILED"

    INDEXING_STARTED = "INDEXING_STARTED"
    INDEXING_COMPLETED = "INDEXING_COMPLETED"
    INDEXING_DEGRADED = "INDEXING_DEGRADED"
    INDEXING_FAILED = "INDEXING_FAILED"

    RETRIEVAL_STARTED = "RETRIEVAL_STARTED"
    RETRIEVAL_COMPLETED = "RETRIEVAL_COMPLETED"
    RETRIEVAL_DEGRADED = "RETRIEVAL_DEGRADED"
    RETRIEVAL_FAILED = "RETRIEVAL_FAILED"

    EVIDENCE_CONSTRUCTION_STARTED = "EVIDENCE_CONSTRUCTION_STARTED"
    EVIDENCE_CONSTRUCTION_COMPLETED = "EVIDENCE_CONSTRUCTION_COMPLETED"
    EVIDENCE_CONSTRUCTION_DEGRADED = "EVIDENCE_CONSTRUCTION_DEGRADED"
    EVIDENCE_CONSTRUCTION_FAILED = "EVIDENCE_CONSTRUCTION_FAILED"

    CONTEXT_CONSTRUCTION_STARTED = "CONTEXT_CONSTRUCTION_STARTED"
    CONTEXT_CONSTRUCTION_COMPLETED = "CONTEXT_CONSTRUCTION_COMPLETED"
    CONTEXT_CONSTRUCTION_DEGRADED = "CONTEXT_CONSTRUCTION_DEGRADED"
    CONTEXT_CONSTRUCTION_FAILED = "CONTEXT_CONSTRUCTION_FAILED"

    EVALUATION_STARTED = "EVALUATION_STARTED"
    EVALUATION_COMPLETED = "EVALUATION_COMPLETED"
    EVALUATION_DEGRADED = "EVALUATION_DEGRADED"
    EVALUATION_FAILED = "EVALUATION_FAILED"
