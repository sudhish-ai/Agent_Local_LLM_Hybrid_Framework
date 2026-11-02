# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the stable source-binding interface used by the ALHF
# Knowledge Foundation production runtime.
#
# Problem Solved:
# Runtime source composition requires a stable boundary connecting the
# original customer source and governed source plan to acquisition binding
# without exposing physical-provider mechanics to ingestion execution.
#
# Responsibilities:
# - Verify the binder interface cannot instantiate directly.
# - Verify concrete implementations satisfy the binder contract.
# - Verify source input and governed plan cross the boundary unchanged.
# - Verify implementations can return KnowledgeSourceBinding.
# - Protect the interface from execution or provider-specific concerns.
#
# Must Not:
# - Configure concrete source adapters.
# - Execute Knowledge acquisition.
# - Test local filesystem behavior.
# - Test ingestion or query execution.
# - Expose provider-specific configuration.

from __future__ import annotations

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
from alhf.rag.runtime.contracts.knowledge_source_input import (
    KnowledgeSourceInput,
)
from alhf.rag.runtime.contracts.knowledge_source_plan import (
    KnowledgeSourcePlan,
)
from alhf.rag.runtime.interfaces.knowledge_source_binder import (
    KnowledgeSourceBinder,
)


class _AcquisitionService(AcquisitionService):
    def acquire(
        self,
        request: AcquisitionRequest,
    ) -> AcquisitionSession:
        raise NotImplementedError


class _TestBinder(KnowledgeSourceBinder):
    def __init__(
        self,
        binding: KnowledgeSourceBinding,
    ) -> None:
        self._binding = binding
        self.received_source: KnowledgeSourceInput | None = None
        self.received_plan: KnowledgeSourcePlan | None = None

    def bind(
        self,
        *,
        source: KnowledgeSourceInput,
        plan: KnowledgeSourcePlan,
    ) -> KnowledgeSourceBinding:
        self.received_source = source
        self.received_plan = plan
        return self._binding


def _plan() -> KnowledgeSourcePlan:
    return KnowledgeSourcePlan(
        source_id="source:test",
        knowledge_scope_ref="scope:test",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="test-adapter",
    )


def _binding() -> KnowledgeSourceBinding:
    source = KnowledgeSource(
        source_id="source:test",
        knowledge_scope_ref="scope:test",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="test-adapter",
    )
    return KnowledgeSourceBinding(
        source=source,
        acquisition_service=_AcquisitionService(),
    )


def test_interface_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        KnowledgeSourceBinder()


def test_concrete_binder_is_binder_contract() -> None:
    binder = _TestBinder(_binding())

    assert isinstance(
        binder,
        KnowledgeSourceBinder,
    )


def test_binding_boundary_preserves_source_and_plan() -> None:
    binding = _binding()
    binder = _TestBinder(binding)
    source = KnowledgeSourceInput(
        source="customer-source",
    )
    plan = _plan()

    result = binder.bind(
        source=source,
        plan=plan,
    )

    assert result is binding
    assert binder.received_source is source
    assert binder.received_plan is plan


def test_interface_exposes_only_binding_responsibility() -> None:
    assert (
        KnowledgeSourceBinder.__abstractmethods__
        == frozenset({"bind"})
    )
