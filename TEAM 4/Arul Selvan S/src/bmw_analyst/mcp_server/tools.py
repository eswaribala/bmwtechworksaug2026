from bmw_analyst.snowflake.executor import execute_query


def _tool_result(tool_name: str, rows: list[dict]) -> dict:
    """Return the normalized tool payload expected by MCP clients and tests."""
    return {
        "success": True,
        "tool": tool_name,
        "data": rows,
    }


# -------------------------------------------------
# Vehicle Sales
# -------------------------------------------------

def get_vehicle_sales() -> dict:
    """
    Return BMW vehicle sales data.
    """

    sql = """
        SELECT
            VEHICLE_ID,
            MODEL,
            CITY,
            SALE_DATE,
            SALES_AMOUNT,
            QUANTITY
        FROM BMW_ANALYTICS.BMW_DATA.BMW_VEHICLE_SALES
        ORDER BY SALE_DATE DESC
        LIMIT 1000
    """

    return _tool_result("get_vehicle_sales", execute_query(sql))


# -------------------------------------------------
# Warranty Cost
# -------------------------------------------------

def get_warranty_cost() -> dict:
    """
    Return BMW warranty cost data.
    """

    sql = """
        SELECT
            VEHICLE_ID,
            MODEL,
            CITY,
            WARRANTY_DATE,
            FAULT_TYPE,
            WARRANTY_COST
        FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
        ORDER BY WARRANTY_DATE DESC
        LIMIT 1000
    """

    return _tool_result("get_warranty_cost", execute_query(sql))


# -------------------------------------------------
# Fault Summary
# -------------------------------------------------

def get_fault_summary() -> dict:
    """
    Return BMW fault summary.
    """

    sql = """
        SELECT
            MODEL,
            CITY,
            FAULT_TYPE,
            SEVERITY,
            COUNT(*) AS FAULT_COUNT
        FROM BMW_ANALYTICS.BMW_DATA.BMW_FAULTS
        GROUP BY
            MODEL,
            CITY,
            FAULT_TYPE,
            SEVERITY
        ORDER BY FAULT_COUNT DESC
        LIMIT 1000
    """

    return _tool_result("get_fault_summary", execute_query(sql))


# -------------------------------------------------
# Battery Status
# -------------------------------------------------

def get_battery_status() -> dict:
    """
    Return BMW battery status.
    """

    sql = """
        SELECT
            VEHICLE_ID,
            MODEL,
            CITY,
            BATTERY_DATE,
            BATTERY_PERCENTAGE,
            BATTERY_STATUS
        FROM BMW_ANALYTICS.BMW_DATA.BMW_BATTERY
        ORDER BY BATTERY_DATE DESC
        LIMIT 1000
    """

    return _tool_result("get_battery_status", execute_query(sql))