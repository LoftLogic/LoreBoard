"""Tool base class and registry. Tools are API wrappers callable by agents."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from src.telemetry.tracer import get_logger

log = get_logger("tools")


class ToolInput(BaseModel):
    pass


class ToolOutput(BaseModel):
    success: bool
    data: Any = None
    error: str | None = None


class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    async def run(self, inputs: ToolInput) -> ToolOutput: ...

    async def __call__(self, inputs: ToolInput) -> ToolOutput:
        log.info("tool.call", tool=self.name, inputs=inputs.model_dump())
        result = await self.run(inputs)
        log.info("tool.result", tool=self.name, success=result.success)
        return result


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]


# Global registry
registry = ToolRegistry()
