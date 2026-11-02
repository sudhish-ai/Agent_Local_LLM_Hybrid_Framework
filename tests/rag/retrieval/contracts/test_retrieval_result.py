# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF RetrievalResult contract.
#
# Responsibilities:
# - Validate provider-neutral retrieval-result construction.
# - Validate representation and Knowledge provenance.
# - Validate logical index identity and version.
# - Validate retrieval score and rank semantics.
# - Validate required text normalization.
# - Validate contract immutability.
#
# Must Not:
# - Test retrieval algorithms or providers.
# - Treat RetrievalResult as validated Evidence.
# - Test reranking, Evidence, Context, or generation.
# - Test adaptive Retrieval Intelligence.
# - Depend on external RAG or orchestration frameworks.

import math
from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.representation.contracts.knowledge_representation import (
    RepresentationKind,
)
from alhf.rag.retrieval.contracts.retrieval_result import (
    RetrievalResult,
)


def _result(
    *,
    score: float = 0.95,
    rank: int = 1,
) -> RetrievalResult:
    return RetrievalResult(
        representation_ref="representation-001",
        representation_kind=RepresentationKind.LEXICAL,
        knowledge_unit_ref="unit-001",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
        index_ref="knowledge-index",
        index_version="v1",
        score=score,
        rank=rank,
    )


def test_create_retrieval_result() -> None:
    result = _result()

    assert result.representation_ref == "representation-001"
    assert result.representation_kind == RepresentationKind.LEXICAL
    assert result.knowledge_unit_ref == "unit-001"
    assert result.score == 0.95
    assert result.rank == 1


def test_result_preserves_knowledge_provenance() -> None:
    result = _result()

    assert result.derivation_id == "derivation-001"
    assert result.knowledge_scope_ref == "scope-001"
    assert result.resource_ref == "resource-001"
    assert result.revision_ref == "revision-001"


def test_result_preserves_index_identity() -> None:
    result = _result()

    assert result.index_ref == "knowledge-index"
    assert result.index_version == "v1"


@pytest.mark.parametrize(
    "kind",
    tuple(RepresentationKind),
)
def test_all_representation_kinds_are_supported(
    kind: RepresentationKind,
) -> None:
    result = RetrievalResult(
        representation_ref="representation-001",
        representation_kind=kind,
        knowledge_unit_ref="unit-001",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
        index_ref="knowledge-index",
        index_version="v1",
        score=1.0,
        rank=1,
    )

    assert result.representation_kind == kind


def test_required_text_is_normalized() -> None:
    result = RetrievalResult(
        representation_ref="  representation-001  ",
        representation_kind=RepresentationKind.LEXICAL,
        knowledge_unit_ref="  unit-001  ",
        derivation_id="  derivation-001  ",
        knowledge_scope_ref="  scope-001  ",
        resource_ref="  resource-001  ",
        revision_ref="  revision-001  ",
        index_ref="  knowledge-index  ",
        index_version="  v1  ",
        score=1,
        rank=1,
    )

    assert result.representation_ref == "representation-001"
    assert result.knowledge_unit_ref == "unit-001"
    assert result.derivation_id == "derivation-001"
    assert result.knowledge_scope_ref == "scope-001"
    assert result.resource_ref == "resource-001"
    assert result.revision_ref == "revision-001"
    assert result.index_ref == "knowledge-index"
    assert result.index_version == "v1"


@pytest.mark.parametrize(
    "score",
    (0, 1, -1, 0.5),
)
def test_finite_numeric_score_is_supported(
    score: float,
) -> None:
    result = _result(
        score=score,
    )

    assert result.score == float(score)


@pytest.mark.parametrize(
    "score",
    (math.inf, -math.inf, math.nan),
)
def test_non_finite_score_is_rejected(
    score: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="score must be finite",
    ):
        _result(
            score=score,
        )


@pytest.mark.parametrize(
    "score",
    (True, "0.5", None),
)
def test_invalid_score_type_is_rejected(
    score: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="score must be a number",
    ):
        _result(
            score=score,
        )


@pytest.mark.parametrize(
    "rank",
    (0, -1),
)
def test_non_positive_rank_is_rejected(
    rank: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="rank must be greater than zero",
    ):
        _result(
            rank=rank,
        )


@pytest.mark.parametrize(
    "rank",
    (True, 1.5, "1", None),
)
def test_invalid_rank_type_is_rejected(
    rank: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="rank must be an int",
    ):
        _result(
            rank=rank,
        )


def test_invalid_representation_kind_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "representation_kind must be an instance of "
            "RepresentationKind"
        ),
    ):
        RetrievalResult(
            representation_ref="representation-001",
            representation_kind="LEXICAL",
            knowledge_unit_ref="unit-001",
            derivation_id="derivation-001",
            knowledge_scope_ref="scope-001",
            resource_ref="resource-001",
            revision_ref="revision-001",
            index_ref="knowledge-index",
            index_version="v1",
            score=1.0,
            rank=1,
        )


def test_retrieval_result_is_immutable() -> None:
    result = _result()

    with pytest.raises(FrozenInstanceError):
        result.rank = 2
