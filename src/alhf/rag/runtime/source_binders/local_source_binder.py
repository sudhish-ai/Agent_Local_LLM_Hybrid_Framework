# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides deterministic local-source binding for the ALHF Knowledge
# Foundation production runtime.
#
# Problem Solved:
# Interpreted local sources must be composed into runtime-ready acquisition
# without exposing filesystem configuration to ingestion execution.
#
# Responsibilities:
# - Bind one validated local source input and governed source plan.
# - Select exact-resource or directory acquisition at the physical edge.
# - Compose the selected adapter behind provider-neutral acquisition.
# - Preserve source-plan identity and customer source intent.
#
# Must Not:
# - Acquire Knowledge resources directly.
# - Parse, normalize, derive, represent, index, or retrieve Knowledge.
# - Leak filesystem branching into KnowledgeIngestionService.
# - Modify frozen local acquisition implementations or contracts.
# - Contain retrieval-mode behavior.
#
# Architectural Position:
# - Local implementation of the stable KnowledgeSourceBinder boundary.
# - Keeps physical local-source composition outside ingestion execution.
#
# Future Extensibility:
# - Other source technologies can provide independent binder implementations.
# - Profiles can supply ALHF-owned physical acquisition bounds.

from __future__ import annotations

from pathlib import Path

from alhf.rag.ingestion.acquisition_service import DefaultAcquisitionService
from alhf.rag.ingestion.contracts.adapter_capabilities import AdapterCapabilities
from alhf.rag.ingestion.contracts.knowledge_source import KnowledgeSourceKind
from alhf.rag.ingestion.providers.in_memory_adapter_registry import (
    InMemoryAdapterRegistry,
)
from alhf.rag.ingestion.providers.local_file_adapter import LocalFileAdapter
from alhf.rag.ingestion.providers.local_resource_adapter import (
    LocalResourceAdapter,
)
from alhf.rag.runtime.contracts.knowledge_source_binding import (
    KnowledgeSourceBinding,
)
from alhf.rag.runtime.contracts.knowledge_source_input import KnowledgeSourceInput
from alhf.rag.runtime.contracts.knowledge_source_plan import KnowledgeSourcePlan
from alhf.rag.runtime.interfaces.knowledge_source_binder import KnowledgeSourceBinder


class LocalSourceBinder(KnowledgeSourceBinder):
    """Compose local sources into provider-neutral acquisition binding."""

    _ADAPTER_REF = "local-file"

    def __init__(
        self,
        *,
        max_resource_bytes: int,
        recursive: bool = True,
    ) -> None:
        self._max_resource_bytes = self._positive_int(
            value=max_resource_bytes,
            field_name="max_resource_bytes",
        )

        if not isinstance(recursive, bool):
            raise TypeError(
                "recursive must be a bool"
            )

        self._recursive = recursive

    def bind(
        self,
        *,
        source: KnowledgeSourceInput,
        plan: KnowledgeSourcePlan,
    ) -> KnowledgeSourceBinding:
        """Bind one interpreted local source to acquisition composition."""

        self._validate_inputs(
            source=source,
            plan=plan,
        )

        path = Path(
            source.source
        ).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(
                "local Knowledge source does not exist"
            )

        adapter = self._adapter(
            path
        )

        registry = InMemoryAdapterRegistry()
        registry.register(
            adapter_ref=self._ADAPTER_REF,
            adapter=adapter,
            capabilities=AdapterCapabilities(),
        )

        return KnowledgeSourceBinding(
            source=plan.to_knowledge_source(),
            acquisition_service=DefaultAcquisitionService(
                registry=registry,
            ),
        )

    def _adapter(
        self,
        path: Path,
    ):
        """Compose physical local acquisition for the exact source scope."""

        if path.is_file():
            return LocalResourceAdapter(
                resource_path=path,
                max_resource_bytes=self._max_resource_bytes,
            )

        if path.is_dir():
            return LocalFileAdapter(
                root_directory=path,
                max_resource_bytes=self._max_resource_bytes,
                recursive=self._recursive,
            )

        raise ValueError(
            "local Knowledge source must be a file or directory"
        )

    @classmethod
    def _validate_inputs(
        cls,
        *,
        source: KnowledgeSourceInput,
        plan: KnowledgeSourcePlan,
    ) -> None:
        """Validate source and interpreted-plan compatibility."""

        if not isinstance(
            source,
            KnowledgeSourceInput,
        ):
            raise TypeError(
                "source must be an instance of KnowledgeSourceInput"
            )

        if not isinstance(
            plan,
            KnowledgeSourcePlan,
        ):
            raise TypeError(
                "plan must be an instance of KnowledgeSourcePlan"
            )

        if plan.source_kind != KnowledgeSourceKind.FILE:
            raise ValueError(
                "local source plan requires FILE source kind"
            )

        if plan.adapter_ref != cls._ADAPTER_REF:
            raise ValueError(
                "local source plan requires local-file adapter_ref"
            )

    @staticmethod
    def _positive_int(
        *,
        value: int,
        field_name: str,
    ) -> int:
        """Validate one positive integer composition bound."""

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

        return value
