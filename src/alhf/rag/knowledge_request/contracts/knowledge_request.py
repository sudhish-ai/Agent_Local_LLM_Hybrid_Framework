# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the stable consumer-facing request boundary for querying the
# ALHF Knowledge Foundation.
#
# Problem Solved:
# Knowledge consumers must not depend directly on retrieval, indexing,
# Evidence, Context-packing, or provider implementation details.
#
# Responsibilities:
# - Identify one Knowledge request.
# - Preserve the target Knowledge scope.
# - Preserve the consumer query.
# - Identify the logical V1 index and version.
# - Define an explicit bounded retrieval limit.
# - Define an explicit bounded Context size.
# - Provide immutable request semantics.
#
# Must Not:
# - Execute retrieval or indexing.
# - Select retrieval or representation providers.
# - Construct Evidence or Context.
# - Contain provider-specific configuration.
# - Generate prompts or invoke models.
# - Implement Retrieval or Context Intelligence.
# - Assume future Standard, Graph, or Agentic retrieval policy.
#
# Architectural Position:
# - Stable entry boundary into the Knowledge query plane.
# - Shields consumers from Knowledge Foundation internals.
# - Provides the request consumed by query orchestration.
#
# Reuse Value:
# - APIs and applications.
# - V3 runtime consumers.
# - Agents and workflows.
# - Local, cloud, and hybrid deployments.
#
# Future Extensibility:
# - Retrieval strategy preferences can evolve through governed contracts.
# - Evidence requirements can evolve independently.
# - Budget and policy controls can compose around this request.
# - Retrieval Intelligence can translate request intent into execution.
# - Knowledge Profiles can hide most fields from end users.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KnowledgeRequest:
    """Immutable request into the ALHF Knowledge query plane."""

    request_id: str
    knowledge_scope_ref: str
    query: str
    index_ref: str
    index_version: str
    retrieval_limit: int
    max_context_bytes: int

    def __post_init__(self) -> None:
        fields = (
            "request_id",
            "knowledge_scope_ref",
            "query",
            "index_ref",
            "index_version",
        )

        for field_name in fields:
            normalized = self._required_text(
                value=getattr(
                    self,
                    field_name,
                ),
                field_name=field_name,
            )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        self._positive_int(
            value=self.retrieval_limit,
            field_name="retrieval_limit",
        )
        self._positive_int(
            value=self.max_context_bytes,
            field_name="max_context_bytes",
        )

    @staticmethod
    def _positive_int(
        *,
        value: int,
        field_name: str,
    ) -> None:
        if isinstance(
            value,
            bool,
        ) or not isinstance(
            value,
            int,
        ):
            raise TypeError(
                f"{field_name} must be an int"
            )

        if value <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero"
            )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
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
