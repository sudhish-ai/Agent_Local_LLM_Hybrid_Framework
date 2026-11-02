# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides deterministic KnowledgeContext evaluation for ALHF RAG V1.
#
# Problem Solved:
# V1 requires a reproducible evaluation baseline that distinguishes a
# Context containing packed Evidence from an empty Context without
# introducing model-based quality judgment or advanced RAG metrics.
#
# Responsibilities:
# - Evaluate KnowledgeContext artifacts.
# - Detect Contexts containing packed Evidence.
# - Detect empty or no-Evidence Contexts.
# - Produce deterministic EvaluationResult artifacts.
# - Preserve evaluated Context identity.
# - Expose stable evaluator identity and version.
#
# Must Not:
# - Claim semantic correctness or factual groundedness.
# - Measure retrieval precision, recall, or relevance quality.
# - Evaluate citation correctness or answer completeness.
# - Generate answers or invoke an LLM.
# - Implement optimization or self-learning.
# - Promote configuration or strategy changes.
# - Depend on external RAG frameworks.
#
# Architectural Position:
# - Concrete V1 implementation of Evaluator.
# - Establishes a deterministic evaluation baseline.
# - Keeps advanced evaluation dimensions independently extensible.
#
# Reuse Value:
# - V1 deterministic Standard RAG evaluation.
# - Empty/no-Evidence Context detection.
# - End-to-end pipeline validation.
# - Regression testing and production diagnostics.
#
# Future Extensibility:
# - Groundedness evaluators can evolve independently.
# - Completeness and citation evaluators remain separate dimensions.
# - Retrieval metrics can evaluate retrieval independently.
# - No-answer evaluation can assess abstention behavior.
# - Knowledge Intelligence can consume evaluation results later.

from __future__ import annotations

import hashlib

from alhf.rag.context_packing.contracts.knowledge_context import (
    KnowledgeContext,
)
from alhf.rag.evaluation.contracts.evaluation_result import (
    EvaluationResult,
    EvaluationStatus,
)
from alhf.rag.evaluation.interfaces.evaluator import (
    Evaluator,
)


class DeterministicContextEvaluator(Evaluator):
    """Evaluate deterministic V1 Knowledge Context presence."""

    _EVALUATOR_REF = "deterministic-context-evaluator"
    _EVALUATOR_VERSION = "1.0"

    @property
    def evaluator_ref(self) -> str:
        return self._EVALUATOR_REF

    @property
    def evaluator_version(self) -> str:
        return self._EVALUATOR_VERSION

    def supports(
        self,
        subject: object,
    ) -> bool:
        return isinstance(
            subject,
            KnowledgeContext,
        )

    def evaluate(
        self,
        *,
        subject: object,
    ) -> EvaluationResult:
        if not self.supports(
            subject
        ):
            raise TypeError(
                "subject must be an instance of KnowledgeContext"
            )

        if (
            subject.evidence_count == 0
            or subject.size_bytes == 0
        ):
            status = EvaluationStatus.INCONCLUSIVE
            score = 0.0
            reason = "Knowledge Context contains no packed Evidence"
        else:
            status = EvaluationStatus.PASS
            score = 1.0
            reason = "Knowledge Context contains packed Evidence"

        return EvaluationResult(
            evaluation_id=self._evaluation_id(
                subject
            ),
            subject_ref=subject.context_id,
            evaluator_ref=self.evaluator_ref,
            evaluator_version=self.evaluator_version,
            status=status,
            score=score,
            reason=reason,
        )

    def _evaluation_id(
        self,
        subject: KnowledgeContext,
    ) -> str:
        material = (
            f"{subject.context_id}|"
            f"{self.evaluator_ref}|"
            f"{self.evaluator_version}|"
            f"{subject.evidence_count}|"
            f"{subject.size_bytes}"
        ).encode("utf-8")

        digest = hashlib.sha256(
            material
        ).hexdigest()

        return f"evaluation:{digest}"
