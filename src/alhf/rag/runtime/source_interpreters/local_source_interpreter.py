# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides deterministic local-filesystem source interpretation for the
# ALHF Knowledge Foundation production runtime.
#
# Problem Solved:
# V1 consumers provide only a local source path. ALHF must validate and
# interpret that source without exposing adapter or source-kind mechanics.
#
# Responsibilities:
# - Accept existing local files and directories.
# - Reject non-local or unavailable source inputs safely.
# - Produce deterministic governed source identity from resolved location.
# - Produce the local-file acquisition plan used by runtime composition.
# - Preserve customer simplicity at the runtime boundary.
#
# Must Not:
# - Acquire or read source contents.
# - Inspect content formats or select parsers.
# - Configure derivation, representation, indexing, or retrieval.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
# - Store credentials or arbitrary configuration dictionaries.
#
# Architectural Position:
# - Concrete V1 KnowledgeSourceInterpreter for local filesystem sources.
# - Sits between source-only customer input and governed ingestion plans.
# - May be replaced or complemented by future source interpreters.
#
# Future Extensibility:
# - Additional source technologies use separate interpreter capabilities.
# - Profile and capability intelligence can select interpreters above here.
# - Downstream Knowledge Foundation contracts remain unchanged.

from __future__ import annotations

import hashlib
from pathlib import Path

from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSourceKind,
)
from alhf.rag.runtime.contracts.knowledge_source_input import (
    KnowledgeSourceInput,
)
from alhf.rag.runtime.contracts.knowledge_source_plan import (
    KnowledgeSourcePlan,
)
from alhf.rag.runtime.interfaces.knowledge_source_interpreter import (
    KnowledgeSourceInterpreter,
)


class LocalSourceInterpreter(KnowledgeSourceInterpreter):
    """Interpret existing local filesystem sources deterministically."""

    _INTERPRETER_REF = "local-source-interpreter"
    _INTERPRETER_VERSION = "1.0"
    _ADAPTER_REF = "local-file"

    def __init__(
        self,
        *,
        knowledge_scope_ref: str = "default",
    ) -> None:
        self._knowledge_scope_ref = self._required_text(
            value=knowledge_scope_ref,
            field_name="knowledge_scope_ref",
        )

    @property
    def interpreter_ref(self) -> str:
        """Return the stable interpreter identifier."""

        return self._INTERPRETER_REF

    @property
    def interpreter_version(self) -> str:
        """Return the stable interpreter behavior version."""

        return self._INTERPRETER_VERSION

    def supports(
        self,
        source: KnowledgeSourceInput,
    ) -> bool:
        """Return whether the source resolves to local filesystem state."""

        if not isinstance(
            source,
            KnowledgeSourceInput,
        ):
            return False

        try:
            return Path(
                source.source
            ).expanduser().exists()
        except (
            OSError,
            ValueError,
        ):
            return False

    def interpret(
        self,
        source: KnowledgeSourceInput,
    ) -> KnowledgeSourcePlan:
        """Interpret one existing local source."""

        if not isinstance(
            source,
            KnowledgeSourceInput,
        ):
            raise TypeError(
                "source must be an instance of "
                "KnowledgeSourceInput"
            )

        if not self.supports(
            source
        ):
            raise ValueError(
                "local Knowledge source does not exist"
            )

        resolved = Path(
            source.source
        ).expanduser().resolve()

        return KnowledgeSourcePlan(
            source_id=self._source_id(
                resolved
            ),
            knowledge_scope_ref=self._knowledge_scope_ref,
            source_kind=KnowledgeSourceKind.FILE,
            adapter_ref=self._ADAPTER_REF,
            configuration_ref=None,
            synchronization_enabled=False,
        )

    @staticmethod
    def _source_id(
        path: Path,
    ) -> str:
        """Build deterministic source identity from resolved location."""

        material = path.as_posix().encode(
            "utf-8"
        )

        return (
            "source:"
            + hashlib.sha256(
                material
            ).hexdigest()
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
