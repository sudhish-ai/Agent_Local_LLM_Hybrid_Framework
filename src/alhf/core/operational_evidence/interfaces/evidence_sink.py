# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal persistence-sink interface used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# Operational Evidence producers must be able to persist evidence without
# depending on JSONL, filesystems, databases, object storage, event
# infrastructure, or any other physical persistence technology.
#
# A stable persistence boundary allows provider implementations to evolve
# independently from evidence producers and Operational Evidence contracts.
#
# Responsibilities:
# - Define the provider-neutral Operational Evidence persistence boundary.
# - Accept validated Operational Evidence records.
# - Return provider-neutral persistence results.
# - Allow persistence providers to be replaced without changing producers.
#
# Must Not:
# - Implement persistence.
# - Contain JSON or JSONL behavior.
# - Contain filesystem or database behavior.
# - Define buffering or batching behavior.
# - Define retry or backpressure behavior.
# - Define retention or rotation behavior.
# - Generate Operational Evidence records.
# - Mutate Operational Evidence records.
# - Contain RAG or Knowledge-specific semantics.
# - Perform failure analysis or root-cause analysis.
# - Expose provider-specific storage locations or identifiers.
#
# Architectural Position:
# - Universal ALHF Operational Evidence interface.
# - Boundary between Operational Evidence producers and persistence
#   providers.
# - Independent from physical storage technology.
#
# Reuse Value:
# - Local JSONL persistence provider.
# - Future database-backed persistence provider.
# - Future object-backed persistence provider.
# - Future distributed persistence provider.
# - Customer-specific Operational Evidence persistence providers.
#
# Future Extensibility:
# - Provider implementations may support batching internally.
# - Provider implementations may support asynchronous delivery internally.
# - Durability policy remains separate from this persistence boundary.
# - Query and repository semantics remain separate responsibilities.
# - Provider capabilities may evolve without changing this interface's
#   core persistence semantics.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.core.operational_evidence.contracts.persistence_result import (
    PersistenceResult,
)
from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)


class EvidenceSink(ABC):
    """
    Universal persistence sink for ALHF Operational Evidence.

    Implementations accept validated Operational Evidence records and
    return provider-neutral persistence results.

    This interface deliberately defines persistence semantics only.
    Physical storage behavior, delivery strategy, batching, buffering,
    retry, durability, and provider-specific diagnostics remain the
    responsibility of concrete implementations and their policies.
    """

    @abstractmethod
    def persist(
        self,
        record: OperationalEvidenceRecord,
    ) -> PersistenceResult:
        """
        Persist one Operational Evidence record.

        Args:
            record:
                Validated immutable Operational Evidence record to persist.

        Returns:
            Provider-neutral result describing the persistence outcome.
        """
        raise NotImplementedError
