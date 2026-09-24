from typing import Any

from pydantic import BaseModel, Field


class MCPResponse(BaseModel):
    success: bool = True
    tool: str
    data: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None


class MCPToolRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)