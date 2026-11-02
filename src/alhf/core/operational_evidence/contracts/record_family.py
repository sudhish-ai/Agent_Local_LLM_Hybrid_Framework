# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal record-family taxonomy used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# ALHF must preserve a strict semantic boundary between facts captured
# during execution and intelligence derived later from those facts.
#
# Failure analysis, root-cause analysis, predictive analysis, corrective
# recommendations, human decisions, executed remediation, and validation
# must remain distinguishable from the operational facts on which they
# depend.
#
# Responsibilities:
# - Classify the semantic family of an ALHF operational-evidence record.
# - Distinguish observed operational events from measurements.
# - Classify derived analytical artifacts.
# - Classify governed human decisions.
# - Classify executed actions.
# - Classify validation outcomes.
# - Provide stable, serialization-friendly record-family values.
#
# Must Not:
# - Define event names for workflows, tasks, agents, or Knowledge stages.
# - Contain RAG or Knowledge-specific semantics.
# - Define failure, severity, retry, or outcome semantics.
# - Define causal relationships.
# - Define persistence, JSON, or JSONL behavior.
# - Define logging behavior.
# - Define analytical algorithms.
# - Define recommendation or remediation logic.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Universal ALHF Operational Evidence contract.
# - Independent from existing ALHF runtime EventType enums.
# - Distinguishes the nature of a record from subsystem event semantics.
#
# Reuse Value:
# - Knowledge Foundation operational evidence.
# - Multi-agent operational evidence.
# - V3 operational evidence.
# - Failure analysis and RCA artifacts.
# - Predictive reliability artifacts.
# - Human-in-the-loop remediation workflows.
# - Post-remediation validation artifacts.
#
# Future Extensibility:
# - Subsystems define governed event vocabularies separately.
# - Knowledge-specific events remain outside this universal taxonomy.
# - Additional record families may be introduced when they represent
#   genuinely different universal semantics.
# - Schema evolution remains separate from record-family classification.

from __future__ import annotations

from enum import Enum


class OperationalRecordFamily(str, Enum):
    """
    Universal semantic families for ALHF operational-evidence records.

    OPERATIONAL_EVENT:
        Represents an observed operational fact about execution.

    MEASUREMENT:
        Represents an objectively measured value whose semantics are
        defined independently from analytical interpretation.

    FINDING:
        Represents an analytical conclusion derived from supporting
        operational evidence.

    PREDICTION:
        Represents an explicitly derived estimate about a future
        condition or behavior.

    RECOMMENDATION:
        Represents a proposed corrective or preventive action derived
        from governed evidence and analysis.

    HUMAN_DECISION:
        Represents a governed human decision associated with a specific
        recommendation or action scope.

    ACTION:
        Represents an action that was actually executed.
        It does not imply that the action was effective.

    VALIDATION:
        Represents a governed validation outcome produced after an
        execution or corrective action.

    These families describe what a record represents. They do not define
    subsystem-specific event names, execution outcomes, causal conclusions,
    persistence behavior, or security policy.
    """

    OPERATIONAL_EVENT = "OPERATIONAL_EVENT"
    MEASUREMENT = "MEASUREMENT"
    FINDING = "FINDING"
    PREDICTION = "PREDICTION"
    RECOMMENDATION = "RECOMMENDATION"
    HUMAN_DECISION = "HUMAN_DECISION"
    ACTION = "ACTION"
    VALIDATION = "VALIDATION"
