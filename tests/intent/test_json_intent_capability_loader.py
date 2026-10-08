# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT

from pathlib import Path

from src.alhf.intent.json_intent_capability_loader import (
    JsonIntentCapabilityLoader,
)


def test_load_missing_file_returns_warning(
    tmp_path: Path,
) -> None:
    loader = (
        JsonIntentCapabilityLoader()
    )

    missing_file = (
        tmp_path / "missing.json"
    )

    result = loader.load(
        missing_file,
    )

    assert not result.loaded_items

    assert (
        len(
            result.warning_messages
        )
        == 1
    )


def test_load_single_mapping(
    tmp_path: Path,
) -> None:
    loader = (
        JsonIntentCapabilityLoader()
    )

    knowledge_asset = (
        tmp_path / "intents.json"
    )

    knowledge_asset.write_text(
        """
{
  "intent_capability_mappings": [
    {
      "intent_id": "hotel_booking",
      "capability_ids": [
        "hotel_search",
        "hotel_booking"
      ]
    }
  ]
}
        """.strip(),
        encoding="utf-8",
    )

    result = loader.load(
        knowledge_asset,
    )

    assert (
        len(
            result.loaded_items
        )
        == 1
    )

    mapping = (
        result.loaded_items[0]
    )

    assert (
        mapping.intent_id
        == "hotel_booking"
    )

    assert (
        mapping.capability_ids
        == (
            "hotel_search",
            "hotel_booking",
        )
    )


def test_load_multiple_mappings(
    tmp_path: Path,
) -> None:
    loader = (
        JsonIntentCapabilityLoader()
    )

    knowledge_asset = (
        tmp_path / "intents.json"
    )

    knowledge_asset.write_text(
        """
{
  "intent_capability_mappings": [
    {
      "intent_id": "hotel_booking",
      "capability_ids": [
        "hotel_search",
        "hotel_booking"
      ]
    },
    {
      "intent_id": "flight_booking",
      "capability_ids": [
        "flight_search",
        "flight_booking"
      ]
    }
  ]
}
        """.strip(),
        encoding="utf-8",
    )

    result = loader.load(
        knowledge_asset,
    )

    assert (
        len(
            result.loaded_items
        )
        == 2
    )

    assert (
        result.loaded_items[0]
        .intent_id
        == "hotel_booking"
    )

    assert (
        result.loaded_items[1]
        .intent_id
        == "flight_booking"
    )


def test_load_preserves_capability_order(
    tmp_path: Path,
) -> None:
    loader = (
        JsonIntentCapabilityLoader()
    )

    knowledge_asset = (
        tmp_path / "intents.json"
    )

    knowledge_asset.write_text(
        """
{
  "intent_capability_mappings": [
    {
      "intent_id": "hotel_booking",
      "capability_ids": [
        "hotel_search",
        "hotel_booking"
      ]
    }
  ]
}
        """.strip(),
        encoding="utf-8",
    )

    result = loader.load(
        knowledge_asset,
    )

    mapping = (
        result.loaded_items[0]
    )

    assert (
        mapping.capability_ids
        == (
            "hotel_search",
            "hotel_booking",
        )
    )


def test_load_returns_no_warnings_for_valid_file(
    tmp_path: Path,
) -> None:
    loader = (
        JsonIntentCapabilityLoader()
    )

    knowledge_asset = (
        tmp_path / "intents.json"
    )

    knowledge_asset.write_text(
        """
{
  "intent_capability_mappings": [
    {
      "intent_id": "hotel_booking",
      "capability_ids": [
        "hotel_search"
      ]
    }
  ]
}
        """.strip(),
        encoding="utf-8",
    )

    result = loader.load(
        knowledge_asset,
    )

    assert (
        result.warning_messages
        == ()
    )
