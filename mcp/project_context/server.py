"""MCP Server for story context, characters, and open questions."""

from typing import Any, Dict, List, Optional
from uuid import UUID
from mcp.base import MCPToolRegistry

registry = MCPToolRegistry("project_context")


@registry.register("get_project_context")
def get_project_context(project_id: UUID) -> Dict[str, Any]:
    """Provides high-level narrative project context."""
    return {
        "project_id": str(project_id),
        "title": "Operation Midnight Sun",
        "genre": "techno-thriller",
        "target_audience": "mature",
        "status": "active",
    }


@registry.register("get_story_summary")
def get_story_summary(project_id: UUID) -> Dict[str, Any]:
    """Provides narrative premise and plot trajectory."""
    return {
        "project_id": str(project_id),
        "summary": "Agent Marcus infiltrates a deep arctic vault to recover stolen biometrics, only to trigger an automated containment sequence.",
        "act_count": 3,
    }


@registry.register("get_character_profile")
def get_character_profile(project_id: UUID, character_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
    """Returns character dramaturg profile and knowledge horizon."""
    return [
        {
            "name": "Marcus Kane",
            "role": "protagonist",
            "traits": ["covert operative", "relentless", "guilt-ridden"],
            "knowledge_horizon": "Unaware that headquarters compromised his escape vector.",
        }
    ]


@registry.register("get_open_questions")
def get_open_questions(project_id: UUID) -> List[str]:
    """Returns current active narrative questions."""
    return [
        "Can Marcus override the blast door before the cryo-venting cycle completes?",
        "Who leaked the extraction frequency to Sector 4?",
    ]
