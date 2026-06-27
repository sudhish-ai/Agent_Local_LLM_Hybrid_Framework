# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

"""Core status and classification enums for ALHF.

This module defines stable enums used across the RAG, Agentic AI, MCP,
local LLM, API, server, security, observability, governance, red-team,
storage, and evaluation layers.

The enums intentionally inherit from str and Enum so values are easy to
serialize into JSON, logs, audit records, telemetry, CLI output, and future
persistent stores.
"""

from __future__ import annotations

from enum import Enum


class PipelineStatus(str, Enum):
    """Standard status returned by pipeline stages.

    These statuses let the framework continue processing large workloads
    without crashing the entire pipeline because of one bad file, failed model
    call, denied access check, or quarantined content.
    """

    SUCCESS = "SUCCESS"
    SKIPPED = "SKIPPED"
    FAILED_RETRYABLE = "FAILED_RETRYABLE"
    FAILED_NON_RETRYABLE = "FAILED_NON_RETRYABLE"
    QUARANTINED = "QUARANTINED"
    ACCESS_DENIED = "ACCESS_DENIED"


class LifecycleState(str, Enum):
    """Lifecycle state for durable framework entities.

    Used for documents, chunks, embeddings, index records, workflow records,
    audit records, and any item that may be updated, deleted, superseded,
    quarantined, or reindexed.
    """

    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    DELETED = "DELETED"
    QUARANTINED = "QUARANTINED"
    FAILED = "FAILED"
    PENDING_REINDEX = "PENDING_REINDEX"


class DataClassification(str, Enum):
    """Generic data classification used across the framework.

    Domain adapters can map these values to domain-specific classifications.
    For example, a hospital adapter may map REGULATED to PHI/ePHI-like data.
    """

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    REGULATED = "REGULATED"


class ErrorSeverity(str, Enum):
    """Severity level for structured errors, telemetry, and audit events."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StageName(str, Enum):
    """Canonical names for major framework pipeline stages."""

    FILE_DISCOVERY = "FILE_DISCOVERY"
    EXTRACTION = "EXTRACTION"
    CLEANING = "CLEANING"
    METADATA_EXTRACTION = "METADATA_EXTRACTION"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INDEXING = "INDEXING"
    RETRIEVAL = "RETRIEVAL"
    RERANKING = "RERANKING"
    CONTEXT_PACKING = "CONTEXT_PACKING"
    GENERATION = "GENERATION"
    EVALUATION = "EVALUATION"
    SECURITY = "SECURITY"
    GUARDRAIL = "GUARDRAIL"
    GOVERNANCE = "GOVERNANCE"
    REDTEAM = "REDTEAM"
    ORCHESTRATION = "ORCHESTRATION"
    MCP_PROTOCOL = "MCP_PROTOCOL"
    LLM_INFERENCE = "LLM_INFERENCE"
    API = "API"
    SERVER = "SERVER"
    STORAGE = "STORAGE"
