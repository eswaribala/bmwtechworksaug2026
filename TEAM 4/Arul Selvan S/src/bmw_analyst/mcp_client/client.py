import json
import os
import sys
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from .models import MCPResponse


class MCPClient:

    def __init__(
        self,
        server_command: str | None = None,
        server_args: list[str] | None = None,
    ):
        self.server_command = server_command or sys.executable

        self.server_args = server_args or [
            "-m",
            "bmw_analyst.mcp_server.server",
        ]

        self._stdio_context = None
        self._session_context = None
        self._session: ClientSession | None = None

    async def _ensure_connected(self) -> ClientSession:
        """
        Start the MCP server and initialize the MCP session once.

        Subsequent tool calls reuse the same process and session.
        """

        if self._session is not None:
            return self._session

        server_env = os.environ.copy()

        server_params = StdioServerParameters(
            command=self.server_command,
            args=self.server_args,
            env=server_env,
        )

        self._stdio_context = stdio_client(server_params)

        streams = await self._stdio_context.__aenter__()

        self._session_context = ClientSession(
            streams[0],
            streams[1],
        )

        self._session = await self._session_context.__aenter__()

        await self._session.initialize()

        return self._session

    async def close(self):
        """
        Gracefully shut down the MCP session and server process.
        """

        if self._session_context is not None:
            try:
                await self._session_context.__aexit__(
                    None,
                    None,
                    None,
                )
            finally:
                self._session_context = None
                self._session = None

        if self._stdio_context is not None:
            try:
                await self._stdio_context.__aexit__(
                    None,
                    None,
                    None,
                )
            finally:
                self._stdio_context = None

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> MCPResponse:

        arguments = arguments or {}

        session = await self._ensure_connected()

        try:

            result = await session.call_tool(
                tool_name,
                arguments,
            )

            data: list[dict[str, Any]] = []

            for content in result.content:

                if not hasattr(content, "text"):
                    continue

                try:
                    parsed = json.loads(content.text)

                except json.JSONDecodeError:
                    continue

                if not isinstance(parsed, dict):
                    continue

                if parsed.get("success") is False:

                    return MCPResponse(
                        success=False,
                        tool=tool_name,
                        error=parsed.get(
                            "error",
                            "MCP tool execution failed.",
                        ),
                    )

                tool_data = parsed.get(
                    "data",
                    [],
                )

                if isinstance(tool_data, list):
                    data = tool_data

            return MCPResponse(
                success=True,
                tool=tool_name,
                data=data,
            )

        except Exception:

            # Reset the session so the next request
            # can create a fresh MCP process/session.

            await self.close()

            raise

    async def get_vehicle_sales(self) -> MCPResponse:
        return await self.call_tool(
            "vehicle_sales"
        )

    async def get_warranty_cost(self) -> MCPResponse:
        return await self.call_tool(
            "warranty_cost"
        )

    async def get_fault_summary(self) -> MCPResponse:
        return await self.call_tool(
            "fault_summary"
        )

    async def get_battery_status(self) -> MCPResponse:
        return await self.call_tool(
            "battery_status"
        )

    async def execute_approved_query(
        self,
        sql: str,
    ) -> MCPResponse:

        return await self.call_tool(
            "execute_approved_query",
            {
                "sql": sql,
            },
        )