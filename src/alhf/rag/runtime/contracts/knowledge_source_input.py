# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the minimal customer-facing Knowledge source input accepted by
# the ALHF Knowledge Foundation runtime.
#
# Problem Solved:
# Runtime consumers must be able to provide a Knowledge source without
# understanding adapters, parsers, providers, indexes, or RAG strategies.
#
# Responsibilities:
# - Preserve exactly one customer-supplied source location.
# - Normalize the source value without interpreting its technology.
# - Provide an immutable boundary for later source interpretation.
# - Keep normal runtime usage independent from technical configuration.
#
# Must Not:
# - Detect source type or content format.
# - Select adapters, parsers, strategies, providers, or indexes.
# - Store credentials, secrets, or arbitrary configuration dictionaries.
# - Perform acquisition, parsing, indexing, retrieval, or evaluation.
# - Encode Standard RAG, GraphRAG, Agentic RAG, or deployment details.
#
# Architectural Position:
# - Stable external input boundary of the Knowledge Foundation runtime.
# - Input to ALHF-owned source interpretation and production composition.
# - Separates customer simplicity from governed internal source contracts.
#
# Future Extensibility:
# - Local paths, URIs, and future source locators remain opaque here.
# - Source interpretation can evolve without changing this contract.
# - Authorization and governed profiles remain separate responsibilities.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KnowledgeSourceInput:
    """Minimal immutable source input supplied to ALHF by a consumer."""

    source: str

    def __post_init__(self) -> None:
        normalized = self._required_text(
            value=self.source,
            field_name="source",
        )

        object.__setattr__(
            self,
            "source",
            normalized,
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
