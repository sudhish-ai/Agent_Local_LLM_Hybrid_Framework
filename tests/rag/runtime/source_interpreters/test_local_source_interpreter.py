# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for deterministic local source interpretation.
#
# Responsibilities:
# - Validate local file and directory support.
# - Validate governed deterministic source planning.
# - Validate missing and invalid source handling.
# - Prove interpretation does not read source contents.
# - Protect the source-only customer runtime boundary.
#
# Must Not:
# - Perform acquisition or parsing.
# - Inspect customer Knowledge content.
# - Configure downstream Knowledge strategies.
# - Introduce Standard RAG, GraphRAG, or Agentic RAG behavior.

from pathlib import Path

import pytest

from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSourceKind,
)
from alhf.rag.runtime.contracts.knowledge_source_input import (
    KnowledgeSourceInput,
)
from alhf.rag.runtime.source_interpreters.local_source_interpreter import (
    LocalSourceInterpreter,
)


def _source(
    path: Path,
) -> KnowledgeSourceInput:
    return KnowledgeSourceInput(
        source=str(path)
    )


def test_interpreter_exposes_stable_identity() -> None:
    interpreter = LocalSourceInterpreter()

    assert (
        interpreter.interpreter_ref
        == "local-source-interpreter"
    )
    assert interpreter.interpreter_version == "1.0"


def test_existing_directory_is_supported(
    tmp_path: Path,
) -> None:
    assert LocalSourceInterpreter().supports(
        _source(tmp_path)
    ) is True


def test_existing_file_is_supported(
    tmp_path: Path,
) -> None:
    path = tmp_path / "policy.pdf"
    path.write_bytes(
        b"test"
    )

    assert LocalSourceInterpreter().supports(
        _source(path)
    ) is True


def test_missing_local_source_is_not_supported(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"

    assert LocalSourceInterpreter().supports(
        _source(missing)
    ) is False


def test_wrong_contract_type_is_not_supported() -> None:
    assert LocalSourceInterpreter().supports(
        "source"
    ) is False


def test_interpret_directory_produces_governed_file_plan(
    tmp_path: Path,
) -> None:
    plan = LocalSourceInterpreter().interpret(
        _source(tmp_path)
    )

    assert plan.knowledge_scope_ref == "default"
    assert plan.source_kind == KnowledgeSourceKind.FILE
    assert plan.adapter_ref == "local-file"
    assert plan.configuration_ref is None
    assert plan.synchronization_enabled is False
    assert plan.source_id.startswith(
        "source:"
    )


def test_interpret_file_produces_governed_file_plan(
    tmp_path: Path,
) -> None:
    path = tmp_path / "policy.pdf"
    path.write_bytes(
        b"test"
    )

    plan = LocalSourceInterpreter().interpret(
        _source(path)
    )

    assert plan.source_kind == KnowledgeSourceKind.FILE
    assert plan.adapter_ref == "local-file"


def test_source_identity_is_deterministic(
    tmp_path: Path,
) -> None:
    interpreter = LocalSourceInterpreter()
    source = _source(
        tmp_path
    )

    first = interpreter.interpret(
        source
    )
    second = interpreter.interpret(
        source
    )

    assert first.source_id == second.source_id


def test_different_locations_produce_different_source_identity(
    tmp_path: Path,
) -> None:
    first_path = tmp_path / "first"
    second_path = tmp_path / "second"

    first_path.mkdir()
    second_path.mkdir()

    interpreter = LocalSourceInterpreter()

    first = interpreter.interpret(
        _source(first_path)
    )
    second = interpreter.interpret(
        _source(second_path)
    )

    assert first.source_id != second.source_id


def test_configured_scope_is_preserved(
    tmp_path: Path,
) -> None:
    plan = LocalSourceInterpreter(
        knowledge_scope_ref="customer-001",
    ).interpret(
        _source(tmp_path)
    )

    assert plan.knowledge_scope_ref == "customer-001"


@pytest.mark.parametrize(
    "value",
    (
        "",
        "   ",
    ),
)
def test_empty_scope_is_rejected(
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="knowledge_scope_ref cannot be empty",
    ):
        LocalSourceInterpreter(
            knowledge_scope_ref=value
        )


def test_non_string_scope_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="knowledge_scope_ref must be a string",
    ):
        LocalSourceInterpreter(
            knowledge_scope_ref=123
        )


def test_interpret_rejects_wrong_contract_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "source must be an instance of "
            "KnowledgeSourceInput"
        ),
    ):
        LocalSourceInterpreter().interpret(
            "source"
        )


def test_interpret_rejects_missing_source(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="local Knowledge source does not exist",
    ):
        LocalSourceInterpreter().interpret(
            _source(
                tmp_path / "missing"
            )
        )


def test_interpretation_does_not_read_file_content(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "policy.pdf"
    path.write_bytes(
        b"customer-content"
    )

    def _fail_read(
        *args,
        **kwargs,
    ):
        raise AssertionError(
            "source interpretation must not read content"
        )

    monkeypatch.setattr(
        Path,
        "read_bytes",
        _fail_read,
    )

    plan = LocalSourceInterpreter().interpret(
        _source(path)
    )

    assert plan.adapter_ref == "local-file"
