# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal serialization interface used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# Operational Evidence records require a representation suitable for
# physical persistence without coupling the universal record contract or
# persistence providers to JSON, JSONL, or another serialization format.
#
# A dedicated serialization boundary allows encoding implementations to
# evolve independently from Operational Evidence semantics and storage
# providers.
#
# Responsibilities:
# - Define provider-neutral serialization of Operational Evidence records.
# - Define deserialization back into Operational Evidence records.
# - Keep serialization format independent from evidence contracts.
# - Preserve the immutable Operational Evidence record abstraction across
#   serialization boundaries.
#
# Must Not:
# - Implement JSON or JSONL serialization.
# - Perform physical persistence.
# - Read or write files.
# - Define storage-provider behavior.
# - Generate or mutate Operational Evidence records.
# - Define schema migration behavior.
# - Define schema compatibility policy.
# - Perform failure analysis or root-cause analysis.
# - Contain RAG or Knowledge-specific semantics.
# - Contain buffering, batching, retry, or retention behavior.
#
# Architectural Position:
# - Universal ALHF Operational Evidence interface.
# - Boundary between semantic Operational Evidence records and encoded
#   physical representations.
# - Independent from the persistence sink and repository implementations.
#
# Reuse Value:
# - Local JSONL Operational Evidence provider.
# - Future database-backed providers.
# - Future object-backed providers.
# - Future archival and migration capabilities.
# - Customer-specific persistence implementations.
#
# Future Extensibility:
# - JSON and other concrete serializers remain separate implementations.
# - Schema compatibility and migration remain separate responsibilities.
# - Serialization implementations may evolve without changing evidence
#   producers or consumers.
# - Physical storage providers may compose a compatible serializer.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)


class EvidenceSerializer(ABC):
    """
    Universal serialization boundary for ALHF Operational Evidence.

    Serialized data is represented as bytes so this interface remains
    independent from text encodings and serialization technologies.

    Implementations are responsible for producing and consuming one
    complete encoded Operational Evidence record.
    """

    @abstractmethod
    def serialize(
        self,
        record: OperationalEvidenceRecord,
    ) -> bytes:
        """
        Serialize one Operational Evidence record.

        Args:
            record:
                Validated immutable Operational Evidence record.

        Returns:
            Complete encoded representation of the record.
        """

        raise NotImplementedError

    @abstractmethod
    def deserialize(
        self,
        payload: bytes,
    ) -> OperationalEvidenceRecord:
        """
        Deserialize one encoded Operational Evidence record.

        Args:
            payload:
                Complete encoded representation of one evidence record.

        Returns:
            Reconstructed immutable Operational Evidence record.
        """

        raise NotImplementedError
