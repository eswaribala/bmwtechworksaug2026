from config.settings import APPROVED_MCP_TOOLS, APPROVED_TABLES


def is_tool_allowed(tool_name: str) -> bool:
    """
    Check whether an MCP tool is approved.
    """
    return tool_name in APPROVED_MCP_TOOLS


def is_table_allowed(table_name: str) -> bool:
    """
    Check whether a Snowflake table is approved.
    """
    return table_name.upper() in APPROVED_TABLES