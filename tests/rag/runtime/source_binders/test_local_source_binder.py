# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies deterministic local-source binding for the ALHF Knowledge
# Foundation production runtime.
#
# Responsibilities:
# - Verify exact-file and directory sources bind to production acquisition.
# - Verify source-plan identity survives binding and acquisition.
# - Verify exact-file binding never acquires sibling resources.
# - Verify local plan compatibility and ALHF-owned bounds.
#
# Must Not:
# - Test parser or downstream Knowledge processing.
# - Duplicate adapter unit-test coverage.
# - Test non-local source technologies.

from __future__ import annotations

from pathlib import Path

import pytest

from alhf.rag.ingestion.contracts.acquisition_request import AcquisitionRequest
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSourceKind,
)
from alhf.rag.runtime.contracts.knowledge_source_input import KnowledgeSourceInput
from alhf.rag.runtime.contracts.knowledge_source_plan import KnowledgeSourcePlan
from alhf.rag.runtime.source_binders.local_source_binder import LocalSourceBinder


def _plan() -> KnowledgeSourcePlan:
    return KnowledgeSourcePlan(
        source_id="source:test",
        knowledge_scope_ref="scope:test",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="local-file",
    )


def _resources(
    binder: LocalSourceBinder,
    source: KnowledgeSourceInput,
):
    binding = binder.bind(
        source=source,
        plan=_plan(),
    )

    session = binding.acquisition_service.acquire(
        AcquisitionRequest(
            source=binding.source,
            max_resources=10,
        )
    )

    return binding, tuple(session.resources()), session.result()


def test_exact_file_binding_acquires_only_requested_resource(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target.txt"
    target.write_bytes(b"target")
    (tmp_path / "sibling.txt").write_bytes(b"sibling")

    binder = LocalSourceBinder(
        max_resource_bytes=1024,
    )

    binding, resources, result = _resources(
        binder,
        KnowledgeSourceInput(
            source=str(target),
        ),
    )

    assert binding.source.source_id == "source:test"
    assert len(resources) == 1
    assert resources[0].resource_ref == "target.txt"
    assert resources[0].content == b"target"
    assert result.acquired_count == 1


def test_directory_binding_uses_collection_acquisition(
    tmp_path: Path,
) -> None:
    (tmp_path / "b.txt").write_bytes(b"b")
    (tmp_path / "a.txt").write_bytes(b"a")

    binder = LocalSourceBinder(
        max_resource_bytes=1024,
    )

    _, resources, result = _resources(
        binder,
        KnowledgeSourceInput(
            source=str(tmp_path),
        ),
    )

    assert tuple(
        resource.resource_ref
        for resource in resources
    ) == (
        "a.txt",
        "b.txt",
    )
    assert result.acquired_count == 2


def test_non_recursive_directory_binding_ignores_nested_resource(
    tmp_path: Path,
) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "nested.txt").write_bytes(b"nested")
    (tmp_path / "root.txt").write_bytes(b"root")

    binder = LocalSourceBinder(
        max_resource_bytes=1024,
        recursive=False,
    )

    _, resources, _ = _resources(
        binder,
        KnowledgeSourceInput(
            source=str(tmp_path),
        ),
    )

    assert tuple(
        resource.resource_ref
        for resource in resources
    ) == (
        "root.txt",
    )


def test_binding_preserves_plan_scope_and_source_identity(
    tmp_path: Path,
) -> None:
    path = tmp_path / "knowledge.txt"
    path.write_bytes(b"knowledge")

    binder = LocalSourceBinder(
        max_resource_bytes=1024,
    )

    binding, resources, _ = _resources(
        binder,
        KnowledgeSourceInput(
            source=str(path),
        ),
    )

    assert binding.source.knowledge_scope_ref == "scope:test"
    assert resources[0].identity.source_ref == "source:test"
    assert resources[0].identity.knowledge_scope_ref == "scope:test"


@pytest.mark.parametrize(
    "max_resource_bytes",
    [0, -1],
)
def test_resource_bound_must_be_positive(
    max_resource_bytes: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="max_resource_bytes must be greater than zero",
    ):
        LocalSourceBinder(
            max_resource_bytes=max_resource_bytes,
        )


def test_recursive_must_be_boolean() -> None:
    with pytest.raises(
        TypeError,
        match="recursive must be a bool",
    ):
        LocalSourceBinder(
            max_resource_bytes=1024,
            recursive="yes",  # type: ignore[arg-type]
        )


def test_rejects_incompatible_source_plan(
    tmp_path: Path,
) -> None:
    path = tmp_path / "knowledge.txt"
    path.write_bytes(b"knowledge")

    plan = KnowledgeSourcePlan(
        source_id="source:test",
        knowledge_scope_ref="scope:test",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="other-adapter",
    )

    with pytest.raises(
        ValueError,
        match="local source plan requires local-file adapter_ref",
    ):
        LocalSourceBinder(
            max_resource_bytes=1024,
        ).bind(
            source=KnowledgeSourceInput(
                source=str(path),
            ),
            plan=plan,
        )
