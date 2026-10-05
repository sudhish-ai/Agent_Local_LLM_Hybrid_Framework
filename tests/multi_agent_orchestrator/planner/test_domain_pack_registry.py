# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validate DomainPackRegistry behavior.
#
# Responsibilities:
# - Validate supported domains.
# - Validate domain pack lookup.
# - Validate unknown domain handling.
#
# Must Not:
# - Test planner logic.
# - Test detector logic.
# - Test workflow generation.
# - Test orchestration behavior.

from unittest import TestCase

from alhf.multi_agent_orchestrator.planner.domain_packs.domain_pack_registry import (
    DomainPackRegistry,
)
from alhf.multi_agent_orchestrator.planner.domain_packs.repository_domain_pack import (
    RepositoryDomainPack,
)


class TestDomainPackRegistry(TestCase):

    def test_supported_domains(self) -> None:
        registry = DomainPackRegistry()

        self.assertIn(
            "software_engineering",
            registry.supported_domains(),
        )

    def test_get_repository_domain_pack(self) -> None:
        registry = DomainPackRegistry()

        domain_pack = registry.get_domain_pack(
            "software_engineering",
        )

        self.assertIsInstance(
            domain_pack,
            RepositoryDomainPack,
        )

    def test_unknown_domain_returns_none(self) -> None:
        registry = DomainPackRegistry()

        domain_pack = registry.get_domain_pack(
            "unknown_domain",
        )

        self.assertIsNone(
            domain_pack,
        )
