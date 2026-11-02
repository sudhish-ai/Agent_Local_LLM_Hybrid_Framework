# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the conservative deterministic failure translator used by
# ALHF Knowledge Foundation production ingestion.
#
# Problem Solved:
# Unclassified stage exceptions must not become governed ingestion
# failure facts through exception-type guessing or message matching.
#
# Responsibilities:
# - Verify valid unclassified failures decline translation.
# - Verify every current ingestion stage remains unclassified.
# - Verify exception type does not manufacture failure semantics.
# - Verify translation inputs are strictly validated.
# - Verify translation does not mutate supplied execution facts.
#
# Must Not:
# - Define resource-isolation classifications.
# - Infer semantics from exception messages.
# - Test execution-policy decisions.
# - Execute retry, continuation, termination, or recovery.
# - Test Operational Evidence behavior.

from __future__ import annotations

import pytest

from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_failure import (
    KnowledgeIngestionStage,
)
from alhf.rag.runtime.failure_translation.deterministic_ingestion_failure_translator import (
    DeterministicIngestionFailureTranslator,
)


def _identity() -> ResourceIdentity:
    return ResourceIdentity(
        knowledge_scope_ref="scope:test",
        source_ref="source:test",
        logical_resource_id="resource:test",
        revision_id="revision:test",
    )


def test_unclassified_failure_declines_translation() -> None:
    translator = DeterministicIngestionFailureTranslator()

    result = translator.translate(
        error=ValueError("unclassified failure"),
        stage=KnowledgeIngestionStage.PARSING,
        identity=_identity(),
    )

    assert result is None


@pytest.mark.parametrize(
    "stage",
    list(KnowledgeIngestionStage),
)
def test_every_current_stage_remains_unclassified(
    stage: KnowledgeIngestionStage,
) -> None:
    translator = DeterministicIngestionFailureTranslator()

    result = translator.translate(
        error=RuntimeError("failure"),
        stage=stage,
        identity=_identity(),
    )

    assert result is None


@pytest.mark.parametrize(
    "error",
    [
        ValueError("failure"),
        TypeError("failure"),
        LookupError("failure"),
        RuntimeError("failure"),
    ],
)
def test_exception_type_does_not_manufacture_semantics(
    error: Exception,
) -> None:
    translator = DeterministicIngestionFailureTranslator()

    result = translator.translate(
        error=error,
        stage=KnowledgeIngestionStage.PARSING,
        identity=_identity(),
    )

    assert result is None


def test_rejects_invalid_error_contract() -> None:
    translator = DeterministicIngestionFailureTranslator()

    with pytest.raises(
        TypeError,
        match="error must be an instance of Exception",
    ):
        translator.translate(
            error="failure",  # type: ignore[arg-type]
            stage=KnowledgeIngestionStage.PARSING,
            identity=_identity(),
        )


def test_rejects_invalid_stage_contract() -> None:
    translator = DeterministicIngestionFailureTranslator()

    with pytest.raises(
        TypeError,
        match="KnowledgeIngestionStage",
    ):
        translator.translate(
            error=RuntimeError("failure"),
            stage="PARSING",  # type: ignore[arg-type]
            identity=_identity(),
        )


def test_rejects_invalid_identity_contract() -> None:
    translator = DeterministicIngestionFailureTranslator()

    with pytest.raises(
        TypeError,
        match="ResourceIdentity",
    ):
        translator.translate(
            error=RuntimeError("failure"),
            stage=KnowledgeIngestionStage.PARSING,
            identity=object(),  # type: ignore[arg-type]
        )


def test_translation_does_not_mutate_execution_facts() -> None:
    translator = DeterministicIngestionFailureTranslator()
    error = RuntimeError("failure")
    identity = _identity()

    translator.translate(
        error=error,
        stage=KnowledgeIngestionStage.INDEXING,
        identity=identity,
    )

    assert str(error) == "failure"
    assert identity.knowledge_scope_ref == "scope:test"
    assert identity.source_ref == "source:test"
    assert identity.resource_ref == "resource:test"
    assert identity.revision_ref == "revision:test"
