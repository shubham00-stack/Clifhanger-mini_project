"""MCP Server for quotes, scenes, and provenance evidence."""

from typing import Any, Dict, List, Optional
from uuid import UUID
from mcp.base import MCPToolRegistry

registry = MCPToolRegistry("evidence")


@registry.register("search_evidence")
def search_evidence(project_id: UUID, query: Optional[str] = None) -> List[Dict[str, Any]]:
    """Searches story text for quotes matching narrative themes."""
    return [
        {
            "quote": "The digital timer flashed 00:03, humming with high-voltage frequency.",
            "location_reference": "Scene 14 / Ending cutoff",
            "relevance": 0.95,
        }
    ]


@registry.register("get_scene")
def get_scene(project_id: UUID, query: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves full scene text by index or heading."""
    return {
        "project_id": str(project_id),
        "heading": "INT. ARCTIC VAULT - CONTINUOUS",
        "content": "Marcus hammered on the reinforced glass. The coolant hissed across the floor.",
    }


@registry.register("get_ending_evidence")
def get_ending_evidence(project_id: UUID) -> List[Dict[str, Any]]:
    """Retrieves verified quotes specifically from the ending scene."""
    return [
        {
            "quote": "The heavy hydraulic bolt engaged. The red lamp died.",
            "evidence_type": "verbatim_quote",
            "location": "ending",
        }
    ]


@registry.register("get_dimension_evidence")
def get_dimension_evidence(project_id: UUID, dimension: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves supporting evidence for a specific scoring dimension."""
    return {
        "dimension": dimension or "urgency",
        "evidence": "Timer counting down with 3 seconds remaining.",
        "epistemic_status": "shared",
    }
