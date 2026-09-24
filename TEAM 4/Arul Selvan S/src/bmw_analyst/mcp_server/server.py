from mcp.server.fastmcp import FastMCP

from config.settings import MCP_SERVER_NAME

from bmw_analyst.security.permissions import is_tool_allowed
from bmw_analyst.security.sql_validator import validate_sql
from bmw_analyst.snowflake.executor import execute_query

from .tools import (
    get_vehicle_sales,
    get_warranty_cost,
    get_fault_summary,
    get_battery_status,
)


# -------------------------------------------------
# MCP Server
# -------------------------------------------------

mcp = FastMCP(MCP_SERVER_NAME)


# -------------------------------------------------
# Vehicle Sales
# -------------------------------------------------

@mcp.tool()
def vehicle_sales() -> dict:
    """
    Get BMW vehicle sales information.
    """

    if not is_tool_allowed("get_vehicle_sales"):
        return {
            "success": False,
            "tool": "get_vehicle_sales",
            "error": "Tool is not approved.",
        }

    try:
        result = get_vehicle_sales()

        return {
            "success": True,
            "tool": "get_vehicle_sales",
            "data": result,
        }

    except Exception as exc:
        return {
            "success": False,
            "tool": "get_vehicle_sales",
            "error": str(exc),
        }


# -------------------------------------------------
# Warranty Cost
# -------------------------------------------------

@mcp.tool()
def warranty_cost() -> dict:
    """
    Get BMW warranty cost information.
    """

    if not is_tool_allowed("get_warranty_cost"):
        return {
            "success": False,
            "tool": "get_warranty_cost",
            "error": "Tool is not approved.",
        }

    try:
        result = get_warranty_cost()

        return {
            "success": True,
            "tool": "get_warranty_cost",
            "data": result,
        }

    except Exception as exc:
        return {
            "success": False,
            "tool": "get_warranty_cost",
            "error": str(exc),
        }


# -------------------------------------------------
# Fault Summary
# -------------------------------------------------

@mcp.tool()
def fault_summary() -> dict:
    """
    Get BMW fault summary information.
    """

    if not is_tool_allowed("get_fault_summary"):
        return {
            "success": False,
            "tool": "get_fault_summary",
            "error": "Tool is not approved.",
        }

    try:
        result = get_fault_summary()

        return {
            "success": True,
            "tool": "get_fault_summary",
            "data": result,
        }

    except Exception as exc:
        return {
            "success": False,
            "tool": "get_fault_summary",
            "error": str(exc),
        }


# -------------------------------------------------
# Battery Status
# -------------------------------------------------

@mcp.tool()
def battery_status() -> dict:
    """
    Get BMW battery status information.
    """

    if not is_tool_allowed("get_battery_status"):
        return {
            "success": False,
            "tool": "get_battery_status",
            "error": "Tool is not approved.",
        }

    try:
        result = get_battery_status()

        return {
            "success": True,
            "tool": "get_battery_status",
            "data": result,
        }

    except Exception as exc:
        return {
            "success": False,
            "tool": "get_battery_status",
            "error": str(exc),
        }


# -------------------------------------------------
# Approved Dynamic SQL
# -------------------------------------------------

@mcp.tool()
def execute_approved_query(sql: str) -> dict:
    """
    Execute an approved read-only BMW analytics query.

    Security flow:

        MCP permission check
              ↓
        SQL validation
              ↓
        Snowflake execution
    """

    # ---------------------------------------------
    # Validate input
    # ---------------------------------------------

    if not sql or not sql.strip():
        return {
            "success": False,
            "tool": "execute_approved_query",
            "error": "SQL query cannot be empty.",
        }

    sql = sql.strip()

    # ---------------------------------------------
    # Check MCP permission
    # ---------------------------------------------

    if not is_tool_allowed(
        "execute_approved_query"
    ):
        return {
            "success": False,
            "tool": "execute_approved_query",
            "error": "Tool is not approved.",
        }

    # ---------------------------------------------
    # Validate SQL
    # ---------------------------------------------

    if not validate_sql(sql):
        return {
            "success": False,
            "tool": "execute_approved_query",
            "error": "SQL validation failed.",
        }

    # ---------------------------------------------
    # Execute Snowflake query
    # ---------------------------------------------

    try:

        data = execute_query(sql)

        return {
            "success": True,
            "tool": "execute_approved_query",
            "data": data,
        }

    except Exception as exc:

        return {
            "success": False,
            "tool": "execute_approved_query",
            "error": str(exc),
        }


# -------------------------------------------------
# MCP Server Entry Point
# -------------------------------------------------

if __name__ == "__main__":
    mcp.run()