# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the bounded acquisition-session implementation used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Knowledge acquisition must expose resources incrementally while also
# producing a terminal AcquisitionResult after the bounded resource
# stream has been consumed.
#
# Responsibilities:
# - Consume acquired resources incrementally from one adapter iterator.
# - Enforce the AcquisitionRequest resource bound.
# - Track the number of resources yielded by the session.
# - Produce terminal bounded acquisition state.
# - Prevent result access before resource consumption completes.
# - Preserve continuation state when more acquisition work remains.
#
# Must Not:
# - Materialize the complete source in memory.
# - Perform physical source acquisition.
# - Resolve or select source adapters.
# - Generate source, resource, or revision identities.
# - Parse or normalize acquired content.
# - Perform chunking, embedding, indexing, or retrieval.
# - Persist synchronization state.
# - Contain provider-specific behavior.
# - Contain Standard RAG, GraphRAG, or Agentic RAG logic.
#
# Architectural Position:
# - Concrete bounded implementation of AcquisitionSession.
# - Sits between acquisition orchestration and streamed resources.
# - Preserves the 50M-document bounded-processing requirement.
#
# Reuse Value:
# - Local acquisition.
# - Cloud acquisition.
# - Resumable ingestion.
# - Incremental synchronization.
# - Deterministic acquisition integration testing.
#
# Future Extensibility:
# - Provider-specific continuation state remains outside this component.
# - Checkpoint persistence remains a separate responsibility.
# - Failure-aware sessions can evolve without changing callers.
# - Asynchronous acquisition can use a separate compatible boundary.

from __future__ import annotations

from collections.abc import Iterator

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.acquisition_request import (
    AcquisitionRequest,
)
from alhf.rag.ingestion.contracts.acquisition_result import (
    AcquisitionResult,
    AcquisitionStatus,
)
from alhf.rag.ingestion.interfaces.acquisition_service import (
    AcquisitionSession,
)


class BoundedAcquisitionSession(AcquisitionSession):
    """Bounded streaming acquisition session."""

    def __init__(
        self,
        *,
        request: AcquisitionRequest,
        resources: Iterator[AcquiredResource],
    ) -> None:
        if not isinstance(
            request,
            AcquisitionRequest,
        ):
            raise TypeError(
                "request must be an instance of AcquisitionRequest"
            )

        if not isinstance(
            resources,
            Iterator,
        ):
            raise TypeError(
                "resources must be an Iterator"
            )

        self._request = request
        self._resources = resources
        self._acquired_count = 0
        self._complete = False
        self._has_more = False

    def resources(self):
        """Yield resources up to the configured acquisition bound."""

        if self._complete:
            raise RuntimeError(
                "acquisition session has already completed"
            )

        while self._acquired_count < self._request.max_resources:
            try:
                resource = next(
                    self._resources
                )
            except StopIteration:
                self._complete = True
                return

            if not isinstance(
                resource,
                AcquiredResource,
            ):
                raise TypeError(
                    "adapter must yield AcquiredResource instances"
                )

            self._validate_resource_scope(
                resource=resource,
            )

            self._acquired_count += 1
            yield resource

        self._has_more = self._detect_remaining_resource()
        self._complete = True

    def result(
        self,
    ) -> AcquisitionResult:
        """Return terminal result after resource consumption completes."""

        if not self._complete:
            raise RuntimeError(
                "acquisition has not completed"
            )

        continuation_ref = (
            self._request.continuation_ref
            if self._has_more
            else None
        )

        if self._has_more and continuation_ref is None:
            continuation_ref = (
                f"{self._request.source_id}:continuation"
            )

        status = (
            AcquisitionStatus.PARTIAL
            if self._has_more
            else AcquisitionStatus.COMPLETED
        )

        return AcquisitionResult(
            source_ref=self._request.source_id,
            status=status,
            acquired_count=self._acquired_count,
            has_more=self._has_more,
            continuation_ref=continuation_ref,
            checkpoint_ref=self._request.checkpoint_ref,
        )

    def _detect_remaining_resource(
        self,
    ) -> bool:
        """Determine whether additional adapter resources remain."""

        try:
            next(
                self._resources
            )
        except StopIteration:
            return False

        return True

    def _validate_resource_scope(
        self,
        *,
        resource: AcquiredResource,
    ) -> None:
        """Validate source and Knowledge-scope continuity."""

        if (
            resource.identity.source_ref
            != self._request.source_id
        ):
            raise ValueError(
                "acquired resource source_ref must match request source"
            )

        if (
            resource.identity.knowledge_scope_ref
            != self._request.knowledge_scope_ref
        ):
            raise ValueError(
                "acquired resource knowledge scope must match request"
            )
