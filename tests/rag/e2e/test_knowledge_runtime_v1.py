# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Production-grade black-box acceptance and live demo for ALHF
# Knowledge Foundation V1.
#
# Problem Solved:
# Validates the complete customer-facing Knowledge Foundation runtime
# against a real enterprise PDF without manually orchestrating internal
# RAG pipeline stages from the acceptance test.
#
# Acceptance Criteria:
# - Consume a real repository-root enterprise PDF.
# - Build the production V1 runtime through ALHF bootstrap only.
# - Require only a customer source for ingestion.
# - Require only a customer question for Knowledge querying.
# - Execute acquisition through indexing using production components.
# - Execute retrieval, Evidence, Context, and evaluation.
# - Display query-relevant Knowledge selected from retrieved Context.
# - Display up to five actual retrieved Knowledge sentences.
# - Show long-running ingestion activity visibly in the console.
# - Preserve hard assertions for production acceptance.
# - Do not depend on a pre-authored expected answer.
#
# Must Not:
# - Construct Knowledge pipeline stages directly.
# - Construct parsers, registries, indexes, or retrievers directly.
# - Generate synthetic PDF or Knowledge content.
# - Hard-code a known answer for the supplied query.
# - Search Context for a predetermined expected answer.
# - Invoke an LLM or claim generative reasoning.
# - Treat V1 deterministic evaluation as semantic quality evaluation.
# - Bypass KnowledgeRuntime or KnowledgeRuntimeBootstrap.
#
# Architectural Position:
# - Final black-box V1 Knowledge Foundation acceptance boundary.
# - Exercises the same simple runtime surface intended for consumers.
# - Validates the deterministic Knowledge layer before LLM integration.
#
# Demo Semantics:
# - KNOWLEDGE ANSWER shows up to five query-relevant sentences selected
#   from the Evidence-backed Context actually returned by ALHF.
# - These are retrieved Knowledge excerpts, not generated LLM answers.
# - Future semantic retrieval and generative intelligence remain outside
#   this V1 acceptance scope.

from __future__ import annotations

import itertools
import re
import sys
import threading
import time
from pathlib import Path

from alhf.rag.runtime.contracts.knowledge_ingestion_result import (
    KnowledgeIngestionStatus,
)
from alhf.rag.runtime.knowledge_runtime_bootstrap import (
    KnowledgeRuntimeBootstrap,
)


_SOURCE = Path(
    "dell-openmanage-enterprise_users-guide19_en-us.pdf"
)

_QUERY = "What is the maximum number of devices supported by openmanage-enterprise?"


_SEPARATOR = "=" * 78
_SECTION = "-" * 78

_RESET = "\033[0m"
_BOLD = "\033[1m"
_CYAN = "\033[96m"
_GREEN = "\033[92m"
_RED = "\033[91m"

_ICON_CYAN = "\033[1;30;106m"
_ICON_YELLOW = "\033[1;30;103m"
_ICON_GREEN = "\033[1;30;102m"
_ICON_MAGENTA = "\033[1;97;105m"

_DOCUMENT = "\U0001F4C4"
_QUESTION = "\u2753"
_SETTINGS = "\u2699\ufe0f"
_SEARCH = "\U0001F50E"
_ANSWER = "\u2705"
_EVIDENCE = "\U0001F4DA"
_SUCCESS = "\U0001F7E2"

_NO_KNOWLEDGE = (
    "No query-relevant Knowledge could be selected."
)


class _Spinner:
    """Display activity until a blocking demo operation completes."""

    def __init__(
        self,
        message: str,
    ) -> None:
        self._message = message
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def __enter__(
        self,
    ) -> "_Spinner":
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        self._thread.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        self._stop.set()

        if self._thread is not None:
            self._thread.join()

        color = (
            _GREEN
            if exc_type is None
            else _RED
        )
        status = (
            "DONE"
            if exc_type is None
            else "FAILED"
        )

        sys.stdout.write(
            f"\r{self._message} "
            f"{_BOLD}{color}{status}{_RESET}   \n"
        )
        sys.stdout.flush()

    def _run(
        self,
    ) -> None:
        for frame in itertools.cycle(
            ("|", "/", "-", "\\")
        ):
            if self._stop.is_set():
                return

            sys.stdout.write(
                f"\r{self._message} "
                f"{_BOLD}{_CYAN}{frame}{_RESET}"
            )
            sys.stdout.flush()

            time.sleep(
                0.12
            )


def _normalized(
    text: str,
) -> str:
    return " ".join(
        text.split()
    )


def _query_terms(
    query: str,
) -> set[str]:
    terms = re.findall(
        r"[a-z0-9]+",
        query.lower(),
    )

    stopwords = {
        "a",
        "an",
        "the",
        "of",
        "to",
        "for",
        "in",
        "on",
    }

    return {
        term
        for term in terms
        if term not in stopwords
        and len(term) > 2
    }


def _top_retrieved_knowledge(
    content: bytes,
    query: str,
    *,
    limit: int = 5,
) -> tuple[str, ...]:
    text = _normalized(
        content.decode("utf-8")
    )

    sentences = [
        item.strip()
        for item in re.split(
            r"(?<=[.!?])\s+",
            text,
        )
        if item.strip()
    ]

    terms = _query_terms(
        query
    )

    ranked: list[
        tuple[int, int, str]
    ] = []

    for position, sentence in enumerate(
        sentences
    ):
        lowered = sentence.lower()

        matches = sum(
            term in lowered
            for term in terms
        )

        if matches > 0:
            ranked.append(
                (
                    matches,
                    -position,
                    sentence,
                )
            )

    ranked.sort(
        reverse=True
    )

    selected: list[str] = []
    seen: set[str] = set()

    for _, _, sentence in ranked:
        key = sentence.lower()

        if key in seen:
            continue

        seen.add(
            key
        )
        selected.append(
            sentence
        )

        if len(selected) == limit:
            break

    return tuple(
        selected
    )


def _print_ingestion(
    result,
) -> None:
    print(
        f"\n{_ICON_YELLOW} {_SETTINGS} {_RESET} "
        "[ALHF] INGESTION"
    )
    print(
        f"   Status               : {result.status.value}"
    )
    print(
        f"   Resources acquired   : {result.acquired_count}"
    )
    print(
        f"   Resources parsed     : {result.parsed_count}"
    )
    print(
        f"   Resources normalized : {result.normalized_count}"
    )
    print(
        f"   Knowledge units      : {result.derived_count}"
    )
    print(
        f"   Representations      : {result.represented_count}"
    )
    print(
        f"   Indexed              : {result.indexed_count}"
    )
    print(
        f"   Failures             : {result.failed_resource_count}"
    )


def _print_query(
    context,
    evaluation,
    answers: tuple[str, ...],
) -> None:
    print(
        f"\n{_SECTION}"
    )

    print(
        f"{_ICON_YELLOW} {_SEARCH} {_RESET} "
        "[ALHF] RETRIEVAL"
    )
    print(
        f"   Evidence found       : {context.evidence_count}"
    )
    print(
        f"   Context bytes        : {context.size_bytes}"
    )
    print(
        f"   Evaluation score     : {evaluation.score}"
    )

    print(
        f"\n{_SECTION}"
    )

    print(
        f"{_ICON_GREEN} {_ANSWER} {_RESET} "
        "[ALHF] KNOWLEDGE ANSWER"
    )

    if not answers:
        print(
            f"   {_NO_KNOWLEDGE}"
        )
    else:
        for number, answer in enumerate(
            answers,
            start=1,
        ):
            print(
                f"   {number}. {answer}"
            )

    print(
        f"\n{_ICON_MAGENTA} {_EVIDENCE} {_RESET} "
        "[ALHF] EVIDENCE"
    )

    print(
        f"   Evidence references  : {context.evidence_count}"
    )


def test_real_pdf_executes_black_box_knowledge_runtime_v1() -> None:
    print(
        f"\n{_SEPARATOR}"
    )

    print(
        "      ALHF KNOWLEDGE FOUNDATION V1 - "
        "LIVE BLACK-BOX DEMO"
    )

    print(
        _SEPARATOR
    )

    print(
        f"\n{_ICON_CYAN} {_DOCUMENT} {_RESET} "
        f"[USER] SOURCE   : {_SOURCE}"
    )

    print(
        f"{_ICON_CYAN} {_QUESTION} {_RESET} "
        f"[USER] QUESTION : {_QUERY}"
    )

    assert _SOURCE.is_file(), (
        f"Acceptance PDF not found: {_SOURCE}"
    )

    print(
        f"\n{_ICON_YELLOW} {_SETTINGS} {_RESET} "
        "[ALHF] Building deterministic V1 "
        "Knowledge runtime..."
    )

    runtime = (
        KnowledgeRuntimeBootstrap().build()
    )

    print(
        f"{_ICON_GREEN} {_ANSWER} {_RESET} "
        "[ALHF] Runtime ready."
    )

    ingestion_message = (
        f"{_ICON_YELLOW} {_SETTINGS} {_RESET} "
        "[ALHF] Ingesting customer Knowledge source..."
    )

    with _Spinner(
        ingestion_message
    ):
        ingestion = runtime.ingest(
            str(_SOURCE)
        )

    _print_ingestion(
        ingestion
    )

    assert (
        ingestion.status
        is KnowledgeIngestionStatus.COMPLETED
    )
    assert ingestion.acquired_count == 1
    assert ingestion.parsed_count == 1
    assert ingestion.normalized_count == 1
    assert ingestion.derived_count > 0

    assert (
        ingestion.represented_count
        == ingestion.derived_count
    )

    assert (
        ingestion.indexed_count
        == ingestion.represented_count
    )

    assert ingestion.failed_resource_count == 0

    print(
        f"\n{_ICON_YELLOW} {_SEARCH} {_RESET} "
        "[ALHF] Executing Knowledge query..."
    )

    context, evaluation = runtime.query(
        _QUERY
    )

    answers = _top_retrieved_knowledge(
        context.content,
        _QUERY,
        limit=2,
    )

    _print_query(
        context,
        evaluation,
        answers,
    )

    assert context.evidence_count > 0
    assert context.size_bytes > 0
    assert context.evidence_refs

    assert answers, (
        _NO_KNOWLEDGE
    )

    assert (
        evaluation.subject_ref
        == context.context_id
    )

    assert evaluation.score == 1.0

    print(
        f"\n{_SECTION}"
    )

    print(
        f"{_ICON_GREEN} {_SUCCESS} {_RESET} "
        "[ALHF] ACCEPTANCE RESULT : PASS"
    )

    print(
        f"{_ICON_GREEN} {_ANSWER} {_RESET} "
        "[ALHF] Query -> Retrieved Knowledge -> "
        "Evidence -> Context : GREEN"
    )

    print(
        f"{_SEPARATOR}\n"
    )
