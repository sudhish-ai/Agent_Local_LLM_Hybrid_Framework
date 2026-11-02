# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines stable Knowledge resource identity for the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Enterprise Knowledge changes over time. ALHF must distinguish the
# logical resource from a specific acquired revision without coupling
# identity to filenames, URLs, storage keys, or source-provider details.
#
# Responsibilities:
# - Identify one logical Knowledge resource.
# - Identify the exact revision acquired for that resource.
# - Preserve the source that owns the logical resource.
# - Preserve the governed Knowledge scope.
# - Normalize and validate identity values.
# - Provide immutable identity suitable for provenance and synchronization.
#
# Must Not:
# - Store Knowledge content.
# - Store filesystem paths, URLs, object keys, or database identifiers.
# - Calculate content hashes.
# - Detect source changes.
# - Decide whether revisions are equivalent.
# - Perform synchronization or acquisition.
# - Perform parsing, chunking, embedding, indexing, or retrieval.
# - Contain provider-specific behavior.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Stable Knowledge identity contract for the ingestion plane.
# - Separates logical resource identity from revision identity.
# - Establishes provenance continuity across changing source content.
#
# Future Extensibility:
# - Revision-generation strategy remains outside this contract.
# - Content fingerprints can be governed by separate contracts.
# - Synchronization can compare revisions without redefining identity.
# - Derivations, Knowledge Units, representations, and index membership
#   can reference this identity without depending on source technology.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResourceIdentity:
    """
    Immutable identity of one acquired Knowledge resource revision.

    knowledge_scope_ref:
        Governed Knowledge scope containing the resource.

    source_ref:
        Stable reference to the logical Knowledge source from which the
        resource was acquired.

    logical_resource_id:
        Stable identity of the logical resource across revisions.

    revision_id:
        Identity of the exact acquired resource revision.

    A logical resource may have many revisions over time. Revision
    identity must therefore never replace logical resource identity.
    """

    knowledge_scope_ref: str
    source_ref: str
    logical_resource_id: str
    revision_id: str

    def __post_init__(self) -> None:
        knowledge_scope_ref = self._normalize_required_text(
            value=self.knowledge_scope_ref,
            field_name="knowledge_scope_ref",
        )
        source_ref = self._normalize_required_text(
            value=self.source_ref,
            field_name="source_ref",
        )
        logical_resource_id = self._normalize_required_text(
            value=self.logical_resource_id,
            field_name="logical_resource_id",
        )
        revision_id = self._normalize_required_text(
            value=self.revision_id,
            field_name="revision_id",
        )

        object.__setattr__(
            self,
            "knowledge_scope_ref",
            knowledge_scope_ref,
        )
        object.__setattr__(
            self,
            "source_ref",
            source_ref,
        )
        object.__setattr__(
            self,
            "logical_resource_id",
            logical_resource_id,
        )
        object.__setattr__(
            self,
            "revision_id",
            revision_id,
        )

    @staticmethod
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize one required identity value."""

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized_value

    @property
    def resource_ref(self) -> str:
        """Return the stable logical resource identity."""

        return self.logical_resource_id

    @property
    def revision_ref(self) -> str:
        """Return the exact acquired revision identity."""

        return self.revision_id
