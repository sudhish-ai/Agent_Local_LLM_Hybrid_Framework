# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the runtime-ready acquisition binding produced after ALHF
# interprets and composes a customer Knowledge source.
#
# Problem Solved:
# Production ingestion requires a configured acquisition capability while
# governed KnowledgeSource contracts must remain independent from physical
# paths, URLs, credentials, provider configuration, and adapter instances.
#
# Responsibilities:
# - Preserve one governed logical KnowledgeSource.
# - Preserve the configured provider-neutral AcquisitionService.
# - Provide a stable boundary between source composition and ingestion.
# - Keep physical source configuration outside execution contracts.
# - Keep ingestion execution independent from concrete source technology.
#
# Must Not:
# - Store customer paths, URLs, credentials, or connection information.
# - Store concrete adapters, registries, or provider configuration.
# - Instantiate source adapters or acquisition services.
# - Define acquisition resource bounds or continuation policy.
# - Select parsers, derivation strategies, representations, or indexes.
# - Execute acquisition or downstream Knowledge processing.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Internal runtime boundary between source composition and ingestion.
# - Produced after source interpretation and provider composition.
# - Consumed by provider-neutral Knowledge ingestion execution.
#
# Future Extensibility:
# - Local, cloud, database, API, and collaboration sources can bind to
#   compatible AcquisitionService implementations.
# - Authorization-aware composition can remain outside this contract.
# - Distributed acquisition can expose the same service boundary.
# - Provider and deployment evolution requires no ingestion redesign.

from __future__ import annotations

from dataclasses import dataclass

from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
)
from alhf.rag.ingestion.interfaces.acquisition_service import (
    AcquisitionService,
)


@dataclass(frozen=True, slots=True)
class KnowledgeSourceBinding:
    """Runtime-ready provider-neutral Knowledge acquisition binding."""

    source: KnowledgeSource
    acquisition_service: AcquisitionService

    def __post_init__(self) -> None:
        if not isinstance(
            self.source,
            KnowledgeSource,
        ):
            raise TypeError(
                "source must be an instance of KnowledgeSource"
            )

        if not isinstance(
            self.acquisition_service,
            AcquisitionService,
        ):
            raise TypeError(
                "acquisition_service must be an instance of "
                "AcquisitionService"
            )
