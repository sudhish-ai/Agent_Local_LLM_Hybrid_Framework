# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal read/query boundary for the
# ALHF Operational Evidence repository.
#
# Problem Solved:
# Failure analysis, root-cause analysis, validation, and future reliability
# intelligence must retrieve Operational Evidence without depending on
# JSONL, databases, object storage, file paths, or provider-specific query
# mechanisms.
#
# Responsibilities:
# - Define storage-independent Operational Evidence retrieval.
# - Support exact lookup by evidence-record identity.
# - Support bounded retrieval by execution identity.
# - Support bounded retrieval by correlation identity.
# - Require deterministic provider results through immutable tuples.
# - Keep analytical consumers independent from physical storage.
#
# Must Not:
# - Persist Operational Evidence.
# - Define JSON or JSONL behavior.
# - Expose file paths, line numbers, row identifiers, or provider offsets.
# - Perform failure analysis or root-cause analysis.
# - Perform predictive analysis.
# - Perform aggregation or statistical analysis.
# - Contain RAG or Knowledge-specific query semantics.
# - Define provider-specific indexing.
# - Materialize unbounded evidence history.
#
# Architectural Position:
# - Universal ALHF Operational Evidence interface.
# - Read-side boundary between evidence consumers and repositories.
# - Independent from the evidence write/sink boundary.
# - Implemented by local and future enterprise persistence providers.
#
# Reuse Value:
# - Failure analysis.
# - Root-cause analysis.
# - Execution reconstruction.
# - Multi-agent diagnostics.
# - Knowledge Foundation diagnostics.
# - V3 diagnostics.
# - Post-remediation validation.
#
# Future Extensibility:
# - Richer query contracts remain separate from this foundational
#   repository interface.
# - Provider-specific query acceleration remains behind implementations.
# - Longitudinal analytical projections remain separate from primary
#   evidence retrieval.
# - Knowledge-specific query capabilities remain outside this universal
#   interface.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)


class EvidenceRepository(ABC):
    """
    Universal read boundary for persisted Operational Evidence.

    Repository implementations may use any compliant physical storage
    technology while preserving these retrieval semantics.

    Collection-returning operations are explicitly bounded. Consumers
    cannot request an unbounded execution or correlation history through
    this interface.
    """

    @abstractmethod
    def get_by_record_id(
        self,
        record_id: str,
    ) -> OperationalEvidenceRecord | None:
        """
        Retrieve one Operational Evidence record by semantic identity.

        Returns None when the repository contains no record with the
        requested identity.
        """

        raise NotImplementedError

    @abstractmethod
    def get_by_execution_id(
        self,
        execution_id: str,
        *,
        limit: int,
    ) -> tuple[OperationalEvidenceRecord, ...]:
        """
        Retrieve a bounded collection of records for one execution.

        Implementations must never return more records than the requested
        positive limit.
        """

        raise NotImplementedError

    @abstractmethod
    def get_by_correlation_id(
        self,
        correlation_id: str,
        *,
        limit: int,
    ) -> tuple[OperationalEvidenceRecord, ...]:
        """
        Retrieve a bounded collection of records for one correlation.

        Implementations must never return more records than the requested
        positive limit.
        """

        raise NotImplementedError
