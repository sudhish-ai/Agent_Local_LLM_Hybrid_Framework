# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the stable failure-translation interface used by ALHF
# Knowledge Foundation production ingestion.
#
# Problem Solved:
# Resource-processing exceptions require a stable translation boundary
# before they may become governed Knowledge ingestion failure facts.
#
# Responsibilities:
# - Verify the translator interface cannot instantiate directly.
# - Verify concrete implementations satisfy the translator contract.
# - Verify understood failures can produce governed failure facts.
# - Verify untranslated failures can be represented explicitly by None.
# - Verify stage and ResourceIdentity reach translation unchanged.
#
# Must Not:
# - Define production failure translation rules.
# - Infer semantics from exception messages.
# - Make ingestion execution-policy decisions.
# - Execute retry, continuation, termination, or recovery.
# - Test Operational Evidence behavior.

from __future__ import annotations

import pytest

from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_failure import (
    KnowledgeIngestionFailure,
    KnowledgeIngestionStage,
)
from alhf.rag.runtime.interfaces.knowledge_ingestion_failure_translator import (
    KnowledgeIngestionFailureTranslator,
)


class _TestTranslator(KnowledgeIngestionFailureTranslator):
    def __init__(
        self,
        result: KnowledgeIngestionFailure | None,
    ) -> None:
        self._result = result
        self.received_error: Exception | None = None
        self.received_stage: KnowledgeIngestionStage | None = None
        self.received_identity: ResourceIdentity | None = None

    def translate(
        self,
        *,
        error: Exception,
        stage: KnowledgeIngestionStage,
        identity: ResourceIdentity,
    ) -> KnowledgeIngestionFailure | None:
        self.received_error = error
        self.received_stage = stage
        self.received_identity = identity
        return self._result


def _identity() -> ResourceIdentity:
    return ResourceIdentity(
        knowledge_scope_ref="scope:test",
        source_ref="source:test",
        logical_resource_id="resource:test",
        revision_id="revision:test",
    )


def _failure() -> KnowledgeIngestionFailure:
    return KnowledgeIngestionFailure(
        knowledge_scope_ref="scope:test",
        source_ref="source:test",
        resource_ref="resource:test",
        revision_ref="revision:test",
        stage=KnowledgeIngestionStage.PARSING,
        error_code="TEST_FAILURE",
        error_message="test failure",
        retryable=False,
    )


def test_interface_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        KnowledgeIngestionFailureTranslator()


def test_concrete_translator_is_translator_contract() -> None:
    translator = _TestTranslator(None)

    assert isinstance(
        translator,
        KnowledgeIngestionFailureTranslator,
    )


def test_translator_can_return_governed_failure_fact() -> None:
    failure = _failure()
    translator = _TestTranslator(failure)
    error = ValueError("failure")
    identity = _identity()

    result = translator.translate(
        error=error,
        stage=KnowledgeIngestionStage.PARSING,
        identity=identity,
    )

    assert result is failure
    assert translator.received_error is error
    assert translator.received_stage is KnowledgeIngestionStage.PARSING
    assert translator.received_identity is identity


def test_translator_can_explicitly_decline_translation() -> None:
    translator = _TestTranslator(None)

    result = translator.translate(
        error=RuntimeError("unknown"),
        stage=KnowledgeIngestionStage.INDEXING,
        identity=_identity(),
    )

    assert result is None


def test_interface_exposes_only_translation_responsibility() -> None:
    assert (
        KnowledgeIngestionFailureTranslator.__abstractmethods__
        == frozenset({"translate"})
    )
