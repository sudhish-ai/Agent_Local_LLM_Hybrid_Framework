# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF JSONL Operational Evidence partition locator.
#
# Responsibilities:
# - Validate discovery of JSONL evidence partitions.
# - Validate deterministic partition ordering.
# - Validate malformed partition-name filtering.
# - Validate unrelated file filtering.
# - Validate missing-directory behavior.
# - Validate provider directory configuration.
# - Validate file-prefix configuration.
#
# Must Not:
# - Test JSONL record reading.
# - Test Operational Evidence decoding.
# - Test repository queries.
# - Test Operational Evidence persistence.
# - Test retention, rotation, or archival behavior.
# - Test RAG or Knowledge-specific semantics.

from pathlib import Path

import pytest

from alhf.core.operational_evidence.providers.jsonl_partition_locator import (
    JsonlPartitionLocator,
)


def test_missing_directory_returns_empty_tuple(
    tmp_path: Path,
) -> None:
    locator = JsonlPartitionLocator(
        tmp_path / "missing",
    )

    partitions = locator.locate()

    assert partitions == ()


def test_empty_directory_returns_empty_tuple(
    tmp_path: Path,
) -> None:
    locator = JsonlPartitionLocator(
        tmp_path,
    )

    assert locator.locate() == ()


def test_locate_single_partition(
    tmp_path: Path,
) -> None:
    partition = tmp_path / "operational_evidence-000001.jsonl"
    partition.write_text(
        "",
        encoding="utf-8",
    )

    locator = JsonlPartitionLocator(
        tmp_path,
    )

    assert locator.locate() == (
        partition,
    )


def test_partitions_are_returned_in_numeric_order(
    tmp_path: Path,
) -> None:
    expected = (
        tmp_path / "operational_evidence-000001.jsonl",
        tmp_path / "operational_evidence-000002.jsonl",
        tmp_path / "operational_evidence-000010.jsonl",
    )

    creation_order = (
        expected[2],
        expected[0],
        expected[1],
    )

    for partition in creation_order:
        partition.write_text(
            "",
            encoding="utf-8",
        )

    locator = JsonlPartitionLocator(
        tmp_path,
    )

    assert locator.locate() == expected


def test_custom_file_prefix_is_supported(
    tmp_path: Path,
) -> None:
    expected = tmp_path / "custom-evidence-000001.jsonl"
    expected.write_text(
        "",
        encoding="utf-8",
    )

    locator = JsonlPartitionLocator(
        tmp_path,
        file_prefix="custom-evidence",
    )

    assert locator.locate() == (
        expected,
    )


def test_file_prefix_is_whitespace_normalized(
    tmp_path: Path,
) -> None:
    expected = tmp_path / "custom-evidence-000001.jsonl"
    expected.write_text(
        "",
        encoding="utf-8",
    )

    locator = JsonlPartitionLocator(
        tmp_path,
        file_prefix="  custom-evidence  ",
    )

    assert locator.locate() == (
        expected,
    )


@pytest.mark.parametrize(
    "filename",
    (
        "operational_evidence-invalid.jsonl",
        "operational_evidence-.jsonl",
        "operational_evidence-000000.jsonl",
        "operational_evidence--1.jsonl",
        "operational_evidence-1.5.jsonl",
        "operational_evidence-abc.jsonl",
    ),
)
def test_malformed_partition_names_are_ignored(
    tmp_path: Path,
    filename: str,
) -> None:
    invalid_partition = tmp_path / filename
    invalid_partition.write_text(
        "",
        encoding="utf-8",
    )

    locator = JsonlPartitionLocator(
        tmp_path,
    )

    assert locator.locate() == ()


@pytest.mark.parametrize(
    "filename",
    (
        "unrelated.txt",
        "operational_evidence-000001.txt",
        "other-000001.jsonl",
        "operational_evidence.jsonl",
    ),
)
def test_unrelated_files_are_ignored(
    tmp_path: Path,
    filename: str,
) -> None:
    path = tmp_path / filename
    path.write_text(
        "",
        encoding="utf-8",
    )

    locator = JsonlPartitionLocator(
        tmp_path,
    )

    assert locator.locate() == ()


def test_directory_matching_partition_pattern_is_ignored(
    tmp_path: Path,
) -> None:
    directory = (
        tmp_path
        / "operational_evidence-000001.jsonl"
    )
    directory.mkdir()

    locator = JsonlPartitionLocator(
        tmp_path,
    )

    assert locator.locate() == ()


def test_valid_partitions_remain_when_invalid_files_exist(
    tmp_path: Path,
) -> None:
    valid = tmp_path / "operational_evidence-000003.jsonl"
    valid.write_text(
        "",
        encoding="utf-8",
    )

    invalid = tmp_path / "operational_evidence-invalid.jsonl"
    invalid.write_text(
        "",
        encoding="utf-8",
    )

    unrelated = tmp_path / "notes.txt"
    unrelated.write_text(
        "",
        encoding="utf-8",
    )

    locator = JsonlPartitionLocator(
        tmp_path,
    )

    assert locator.locate() == (
        valid,
    )


@pytest.mark.parametrize(
    "directory",
    (
        "",
        "   ",
    ),
)
def test_directory_rejects_empty_string(
    directory: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="directory cannot be empty",
    ):
        JsonlPartitionLocator(
            directory,
        )


def test_directory_rejects_invalid_type() -> None:
    with pytest.raises(
        TypeError,
        match="directory must be a string or Path",
    ):
        JsonlPartitionLocator(
            123,
        )


def test_existing_non_directory_is_rejected_on_locate(
    tmp_path: Path,
) -> None:
    path = tmp_path / "not-a-directory"
    path.write_text(
        "content",
        encoding="utf-8",
    )

    locator = JsonlPartitionLocator(
        path,
    )

    with pytest.raises(
        NotADirectoryError,
        match=(
            "Operational Evidence location is not a directory"
        ),
    ):
        locator.locate()


@pytest.mark.parametrize(
    "file_prefix",
    (
        "",
        "   ",
    ),
)
def test_file_prefix_rejects_empty_value(
    tmp_path: Path,
    file_prefix: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="file_prefix cannot be empty",
    ):
        JsonlPartitionLocator(
            tmp_path,
            file_prefix=file_prefix,
        )


def test_file_prefix_rejects_non_string_value(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match="file_prefix must be a string",
    ):
        JsonlPartitionLocator(
            tmp_path,
            file_prefix=123,
        )
