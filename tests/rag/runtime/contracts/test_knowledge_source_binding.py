# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the runtime-ready acquisition binding used by the ALHF
# Knowledge Foundation production runtime.
#
# Problem Solved:
# Source composition must provide ingestion with a governed logical source
# and provider-neutral acquisition capability without leaking physical
# source configuration into the execution boundary.
#
# Responsibilities:
# - Verify KnowledgeSource preservation.
# - Verify AcquisitionService preservation.
# - Verify strict source and service contract validation.
# - Verify immutable binding semantics.
# - Protect the provider-neutral source-binding boundary.
#
# Must Not:
# - Configure concrete acquisition adapters.
# - Store or test customer paths, URLs, or credentials.
# - Execute Knowledge acquisition.
# - Test source interpretation.
# - Test ingestion execution or downstream Knowledge stages.

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.ingestion.contracts.acquisition_request import (
    AcquisitionRequest,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)
from alhf.rag.ingestion.interfaces.acquisition_service import (
    AcquisitionService,
    AcquisitionSession,
)
from alhf.rag.runtime.contracts.knowledge_source_binding import (
    KnowledgeSourceBinding,
)


class _AcquisitionService(AcquisitionService):
    def acquire(
        self,
        request: AcquisitionRequest,
    ) -> AcquisitionSession:
        raise NotImplementedError


def _source() -> KnowledgeSource:
    return KnowledgeSource(
        source_id="source:test",
        knowledge_scope_ref="scope:test",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="test-adapter",
    )


def test_preserves_runtime_ready_binding() -> None:
    source = _source()
    service = _AcquisitionService()

    binding = KnowledgeSourceBinding(
        source=source,
        acquisition_service=service,
    )

    assert binding.source is source
    assert binding.acquisition_service is service


def test_rejects_invalid_source_contract() -> None:
    with pytest.raises(
        TypeError,
        match="source must be an instance of KnowledgeSource",
    ):
        KnowledgeSourceBinding(
            source=object(),  # type: ignore[arg-type]
            acquisition_service=_AcquisitionService(),
        )


@pytest.mark.parametrize(
    "service",
    [
        None,
        object(),
        "acquisition-service",
    ],
)
def test_rejects_invalid_acquisition_service_contract(
    service: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="AcquisitionService",
    ):
        KnowledgeSourceBinding(
            source=_source(),
            acquisition_service=service,  # type: ignore[arg-type]
        )


def test_binding_is_immutable() -> None:
    binding = KnowledgeSourceBinding(
        source=_source(),
        acquisition_service=_AcquisitionService(),
    )

    with pytest.raises(FrozenInstanceError):
        binding.source = _source()  # type: ignore[misc]


def test_binding_exposes_only_runtime_acquisition_fields() -> None:
    assert tuple(
        KnowledgeSourceBinding.__dataclass_fields__
    ) == (
        "source",
        "acquisition_service",
    )
