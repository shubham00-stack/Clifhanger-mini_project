"""Model Context Protocol (MCP) server package."""

from .project_context.server import registry as project_context_registry
from .evidence.server import registry as evidence_registry
from .scoring.server import registry as scoring_registry
from .rewrite.server import registry as rewrite_registry

__all__ = [
    "project_context_registry",
    "evidence_registry",
    "scoring_registry",
    "rewrite_registry",
]
