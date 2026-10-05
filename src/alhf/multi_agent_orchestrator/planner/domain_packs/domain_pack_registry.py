# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Central registry for planner domain packs.
#
# Responsibilities:
# - Register domain packs.
# - Discover domain packs.
# - Provide planner access to domain knowledge.
# - Act as the planner domain lookup layer.
#
# Must Not:
# - Contain planning logic.
# - Contain detection logic.
# - Contain workflow generation logic.
# - Contain orchestration logic.

from alhf.multi_agent_orchestrator.planner.domain_packs.repository_domain_pack import (
    RepositoryDomainPack,
)


class DomainPackRegistry:
    """
    Planner domain pack registry.
    """

    def __init__(
        self,
    ) -> None:
        self._domain_packs = {
            "software_engineering": RepositoryDomainPack(),
        }

    def get_domain_pack(
        self,
        domain: str,
    ):
        return self._domain_packs.get(
            domain,
        )

    def supported_domains(
            self,
    ) -> list[str]:
        return list(
            self._domain_packs)
