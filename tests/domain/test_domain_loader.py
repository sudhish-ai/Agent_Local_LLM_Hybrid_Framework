# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for DomainLoader.
#
# Responsibilities:
# - Validate filesystem-based domain loading.
# - Validate successful domain loading.
# - Validate warning generation.
# - Validate failure handling.
# - Validate LoaderResult integration.
#
# Must Not:
# - Test DomainRegistry behavior.
# - Test orchestration behavior.
# - Test planner behavior.
# - Depend on external services.
#
# Architectural Position:
# - Protects the first concrete loader implementation.
# - Validates DomainDefinition creation.
# - Validates BaseLoader compliance.
#
# Reuse Value:
# - Serves as a reference implementation
#   for future loader test suites.
#
# Future Extensibility:
# - YAML support.
# - Marketplace packages.
# - Database-backed domain definitions.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from pathlib import Path

from src.alhf.domain.domain_loader import (
    DomainLoader,
)


def test_load_returns_empty_result_when_path_missing(
    tmp_path: Path,
) -> None:
    loader = DomainLoader()

    missing_path = (
        tmp_path
        / "does_not_exist"
    )

    result = loader.load(
        missing_path
    )

    assert result.loaded_count == 0
    assert result.failed_count == 0
    assert result.has_warnings is True


def test_load_returns_warning_when_source_is_file(
    tmp_path: Path,
) -> None:
    loader = DomainLoader()

    file_path = (
        tmp_path
        / "source.txt"
    )

    file_path.write_text(
        "invalid source",
        encoding="utf-8",
    )

    result = loader.load(
        file_path
    )

    assert result.loaded_count == 0
    assert result.has_warnings is True


def test_load_single_domain_successfully(
    tmp_path: Path,
) -> None:
    loader = DomainLoader()

    domain_dir = (
        tmp_path
        / "travel"
    )

    domain_dir.mkdir()

    domain_file = (
        domain_dir
        / "domain.json"
    )

    domain_file.write_text(
        """
        {
            "domain_id": "travel",
            "domain_name": "Travel",
            "description": "Travel domain."
        }
        """,
        encoding="utf-8",
    )

    result = loader.load(
        tmp_path
    )

    assert result.loaded_count == 1
    assert result.failed_count == 0

    domain = result.loaded_items[0]

    assert domain.domain_id == "travel"
    assert domain.domain_name == "Travel"


def test_load_multiple_domains_successfully(
    tmp_path: Path,
) -> None:
    loader = DomainLoader()

    travel_dir = (
        tmp_path
        / "travel"
    )

    travel_dir.mkdir()

    (
        travel_dir
        / "domain.json"
    ).write_text(
        """
        {
            "domain_id": "travel",
            "domain_name": "Travel",
            "description": "Travel domain."
        }
        """,
        encoding="utf-8",
    )

    finance_dir = (
        tmp_path
        / "finance"
    )

    finance_dir.mkdir()

    (
        finance_dir
        / "domain.json"
    ).write_text(
        """
        {
            "domain_id": "finance",
            "domain_name": "Finance",
            "description": "Finance domain."
        }
        """,
        encoding="utf-8",
    )

    result = loader.load(
        tmp_path
    )

    assert result.loaded_count == 2


def test_missing_domain_file_generates_warning(
    tmp_path: Path,
) -> None:
    loader = DomainLoader()

    orphan_directory = (
        tmp_path
        / "travel"
    )

    orphan_directory.mkdir()

    result = loader.load(
        tmp_path
    )

    assert result.has_warnings is True
    assert result.loaded_count == 0


def test_invalid_json_creates_failed_identifier(
    tmp_path: Path,
) -> None:
    loader = DomainLoader()

    domain_dir = (
        tmp_path
        / "travel"
    )

    domain_dir.mkdir()

    (
        domain_dir
        / "domain.json"
    ).write_text(
        "{ invalid json }",
        encoding="utf-8",
    )

    result = loader.load(
        tmp_path
    )

    assert result.failed_count == 1
    assert (
        "travel"
        in result.failed_identifiers
    )


def test_missing_required_field_creates_failure(
    tmp_path: Path,
) -> None:
    loader = DomainLoader()

    domain_dir = (
        tmp_path
        / "travel"
    )

    domain_dir.mkdir()

    (
        domain_dir
        / "domain.json"
    ).write_text(
        """
        {
            "domain_name": "Travel",
            "description": "Travel domain."
        }
        """,
        encoding="utf-8",
    )

    result = loader.load(
        tmp_path
    )

    assert result.failed_count == 1


def test_metadata_is_loaded(
    tmp_path: Path,
) -> None:
    loader = DomainLoader()

    domain_dir = (
        tmp_path
        / "travel"
    )

    domain_dir.mkdir()

    (
        domain_dir
        / "domain.json"
    ).write_text(
        """
        {
            "domain_id": "travel",
            "domain_name": "Travel",
            "description": "Travel domain.",
            "metadata": {
                "owner": "ALHF"
            }
        }
        """,
        encoding="utf-8",
    )

    result = loader.load(
        tmp_path
    )

    domain = result.loaded_items[0]

    assert (
        domain.metadata["owner"]
        == "ALHF"
    )


def test_version_defaults_to_one_point_zero(
    tmp_path: Path,
) -> None:
    loader = DomainLoader()

    domain_dir = (
        tmp_path
        / "travel"
    )

    domain_dir.mkdir()

    (
        domain_dir
        / "domain.json"
    ).write_text(
        """
        {
            "domain_id": "travel",
            "domain_name": "Travel",
            "description": "Travel domain."
        }
        """,
        encoding="utf-8",
    )

    result = loader.load(
        tmp_path
    )

    domain = result.loaded_items[0]

    assert domain.version == "1.0"


def test_explicit_version_is_loaded(
    tmp_path: Path,
) -> None:
    loader = DomainLoader()

    domain_dir = (
        tmp_path
        / "travel"
    )

    domain_dir.mkdir()

    (
        domain_dir
        / "domain.json"
    ).write_text(
        """
        {
            "domain_id": "travel",
            "domain_name": "Travel",
            "description": "Travel domain.",
            "version": "2.0"
        }
        """,
        encoding="utf-8",
    )

    result = loader.load(
        tmp_path
    )

    domain = result.loaded_items[0]

    assert domain.version == "2.0"
