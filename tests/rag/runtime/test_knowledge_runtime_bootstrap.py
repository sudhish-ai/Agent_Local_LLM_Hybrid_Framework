# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies deterministic V1 Knowledge runtime production composition.
#
# Responsibilities:
# - Verify bootstrap returns the public KnowledgeRuntime boundary.
# - Verify independently built runtimes do not share mutable state.
# - Verify bootstrap-built runtime accepts the simple consumer API.
#
# Must Not:
# - Re-test the complete Knowledge pipeline.
# - Replace the real PDF black-box E2E acceptance test.

from pathlib import Path

from alhf.rag.runtime.knowledge_runtime import KnowledgeRuntime
from alhf.rag.runtime.knowledge_runtime_bootstrap import (
    KnowledgeRuntimeBootstrap,
)


def test_build_returns_knowledge_runtime() -> None:
    runtime = KnowledgeRuntimeBootstrap().build()

    assert isinstance(
        runtime,
        KnowledgeRuntime,
    )


def test_build_returns_independent_runtime_instances() -> None:
    bootstrap = KnowledgeRuntimeBootstrap()

    first = bootstrap.build()
    second = bootstrap.build()

    assert first is not second


def test_bootstrap_runtime_ingests_real_local_text_source(
    tmp_path: Path,
) -> None:
    source = tmp_path / "knowledge.txt"
    source.write_text(
        "OpenManage Enterprise supports managed devices.",
        encoding="utf-8",
    )

    runtime = KnowledgeRuntimeBootstrap().build()

    result = runtime.ingest(
        str(source)
    )

    assert result.acquired_count == 1
    assert result.parsed_count == 1
    assert result.normalized_count == 1
    assert result.derived_count >= 1
    assert result.represented_count >= 1
    assert result.indexed_count >= 1
    assert result.failed_resource_count == 0


def test_bootstrap_runtime_query_uses_shared_ingested_state(
    tmp_path: Path,
) -> None:
    source = tmp_path / "knowledge.txt"
    source.write_text(
        "OpenManage Enterprise supports managed devices.",
        encoding="utf-8",
    )

    runtime = KnowledgeRuntimeBootstrap().build()

    runtime.ingest(
        str(source)
    )

    context, evaluation = runtime.query(
        "managed devices"
    )

    assert context.evidence_count >= 1
    assert context.size_bytes > 0
    assert evaluation.subject_ref == context.context_id
