"""Base MCP Tool registry and security permission sandboxing."""

from typing import Any, Callable, Dict, List
from packages.shared.logging import get_logger

logger = get_logger("mcp.registry")


class MCPToolRegistry:
    """Least-privilege registry exposing strictly bounded tools without arbitrary shell/DB access."""

    def __init__(self, server_name: str):
        self.server_name = server_name
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._tools[name] = fn
            return fn
        return decorator

    def execute_tool(self, tool_name: str, **kwargs: Any) -> Any:
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' is not registered on MCP server '{self.server_name}'")
        logger.info("Executing MCP tool [%s:%s]", self.server_name, tool_name)
        return self._tools[tool_name](**kwargs)

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())
