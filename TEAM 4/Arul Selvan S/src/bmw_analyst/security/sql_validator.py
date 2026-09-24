import re

from config.settings import APPROVED_TABLES, BLOCKED_SQL_COMMANDS


APPROVED_DATABASE = "BMW_ANALYTICS"
APPROVED_SCHEMA = "BMW_DATA"


APPROVED_COLUMNS = {
    "BMW_VEHICLE_SALES": {
        "VEHICLE_ID",
        "MODEL",
        "CITY",
        "SALE_DATE",
        "SALES_AMOUNT",
        "QUANTITY",
    },
    "BMW_WARRANTY": {
        "VEHICLE_ID",
        "MODEL",
        "CITY",
        "WARRANTY_DATE",
        "FAULT_TYPE",
        "WARRANTY_COST",
    },
    "BMW_FAULTS": {
        "VEHICLE_ID",
        "MODEL",
        "CITY",
        "FAULT_DATE",
        "FAULT_TYPE",
        "SEVERITY",
    },
    "BMW_BATTERY": {
        "VEHICLE_ID",
        "MODEL",
        "CITY",
        "BATTERY_DATE",
        "BATTERY_PERCENTAGE",
        "BATTERY_STATUS",
    },
}


SQL_KEYWORDS = {
    "SELECT",
    "FROM",
    "WHERE",
    "GROUP",
    "BY",
    "ORDER",
    "ASC",
    "DESC",
    "LIMIT",
    "OFFSET",
    "HAVING",
    "AS",
    "AND",
    "OR",
    "NOT",
    "IN",
    "IS",
    "NULL",
    "LIKE",
    "BETWEEN",
    "CASE",
    "WHEN",
    "THEN",
    "ELSE",
    "END",
    "DISTINCT",
    "JOIN",
    "INNER",
    "LEFT",
    "RIGHT",
    "FULL",
    "OUTER",
    "ON",
    "UNION",
    "ALL",
    "OVER",
    "PARTITION",
    "ROWS",
    "RANGE",
    "CURRENT",
    "ROW",
}


SQL_FUNCTIONS = {
    "SUM",
    "AVG",
    "MIN",
    "MAX",
    "COUNT",
    "COUNT_IF",
    "COALESCE",
    "ROUND",
    "UPPER",
    "LOWER",
    "DATE_TRUNC",
    "YEAR",
    "MONTH",
    "DAY",
}


def _remove_strings(sql: str) -> str:
    """Remove SQL string literals before identifier analysis."""

    return re.sub(
        r"'(?:''|[^'])*'",
        " ",
        sql,
    )


def _extract_tables(sql: str) -> set[str] | None:
    """
    Extract tables from FROM/JOIN clauses.

    Allowed:

        BMW_VEHICLE_SALES

        BMW_DATA.BMW_VEHICLE_SALES

        BMW_ANALYTICS.BMW_DATA.BMW_VEHICLE_SALES

    The table must always be in APPROVED_TABLES.
    """

    tables = set()

    pattern = re.compile(
        r"\b(?:FROM|JOIN)\s+"
        r"(?:(?:([A-Z0-9_]+)\.)?"
        r"(?:(?:([A-Z0-9_]+)\.)?))?"
        r"([A-Z][A-Z0-9_]*)\b",
        re.IGNORECASE,
    )

    for match in pattern.finditer(sql):
        database = match.group(1)
        schema = match.group(2)
        table = match.group(3)

        if not table:
            return None

        database = database.upper() if database else None
        schema = schema.upper() if schema else None
        table = table.upper()

        # Table itself must be approved.
        if table not in APPROVED_TABLES:
            return None

        # Unqualified table:
        #
        # FROM BMW_WARRANTY
        #
        # Allowed because Snowflake connection already
        # sets BMW_ANALYTICS.BMW_DATA.
        if database is None and schema is None:
            tables.add(table)
            continue

        # Two-part name:
        #
        # BMW_DATA.BMW_WARRANTY
        #
        if database is None and schema is not None:
            if schema != APPROVED_SCHEMA:
                return None

            tables.add(table)
            continue

        # Three-part name:
        #
        # BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
        #
        if database != APPROVED_DATABASE:
            return None

        if schema != APPROVED_SCHEMA:
            return None

        tables.add(table)

    if not tables:
        return None

    return tables


def _extract_aliases(sql: str) -> set[str]:
    """
    Extract SELECT aliases.

    Example:

        SUM(sales_amount) AS total_sales

    total_sales is an output alias and is not a physical
    Snowflake column.
    """

    aliases = set()

    pattern = re.compile(
        r"\bAS\s+([A-Z][A-Z0-9_]*)\b",
        re.IGNORECASE,
    )

    for match in pattern.finditer(sql):
        aliases.add(match.group(1).upper())

    return aliases


def _extract_table_aliases(sql: str) -> set[str]:
    """
    Extract table aliases.

    Examples:

        FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY w

        FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY AS w
    """

    aliases = set()

    pattern = re.compile(
        r"\b(?:FROM|JOIN)\s+"
        r"(?:(?:[A-Z0-9_]+)\.){2}"
        r"[A-Z0-9_]+"
        r"(?:\s+AS)?\s+"
        r"([A-Z][A-Z0-9_]*)\b",
        re.IGNORECASE,
    )

    for match in pattern.finditer(sql):
        aliases.add(match.group(1).upper())

    return aliases


def _columns_are_allowed(
    sql: str,
    approved_tables: set[str],
) -> bool:
    """
    Verify that identifiers used as columns are approved.

    SQL keywords, functions, aliases, database/schema names,
    and approved table names are ignored.
    """

    cleaned_sql = _remove_strings(sql)

    identifiers = {
        token.upper()
        for token in re.findall(
            r"\b[A-Za-z_][A-Za-z0-9_]*\b",
            cleaned_sql,
        )
    }

    allowed_columns = set()

    for table in approved_tables:
        allowed_columns.update(
            APPROVED_COLUMNS[table]
        )

    ignored_identifiers = (
        SQL_KEYWORDS
        | SQL_FUNCTIONS
        | APPROVED_TABLES
        | {
            APPROVED_DATABASE,
            APPROVED_SCHEMA,
        }
    )

    # SELECT aliases.
    ignored_identifiers.update(
        _extract_aliases(sql)
    )

    # Table aliases.
    ignored_identifiers.update(
        _extract_table_aliases(sql)
    )

    for identifier in identifiers:

        if identifier in ignored_identifiers:
            continue

        if identifier in allowed_columns:
            continue

        # COUNT(*) is allowed.
        # '*' does not appear in the identifier set,
        # so no additional handling is required.

        # Unknown identifier.
        return False

    return True


def validate_sql(sql: str) -> bool:
    """
    Validate SQL before execution.

    Security rules:

    1. SQL must not be empty.
    2. Exactly one statement is allowed.
    3. SELECT only.
    4. Dangerous SQL commands are blocked.
    5. Only approved BMW tables are allowed.
    6. Only BMW_ANALYTICS.BMW_DATA is allowed when
       database/schema are explicitly specified.
    7. Only approved BMW columns are allowed.
    """

    if not sql or not sql.strip():
        return False

    sql = sql.strip()

    # Allow exactly one trailing semicolon.
    if sql.endswith(";"):
        sql = sql[:-1].strip()

    # No additional statements.
    if ";" in sql:
        return False

    # SELECT only.
    if not re.match(
        r"^SELECT\b",
        sql,
        re.IGNORECASE,
    ):
        return False

    # Existing blocked commands.
    for command in BLOCKED_SQL_COMMANDS:
        if re.search(
            rf"\b{re.escape(command)}\b",
            sql,
            re.IGNORECASE,
        ):
            return False

    # Additional dangerous commands.
    dangerous_commands = {
        "CALL",
        "USE",
        "SET",
        "EXECUTE",
        "EXEC",
        "COPY",
        "PUT",
        "GET",
        "REMOVE",
    }

    for command in dangerous_commands:
        if re.search(
            rf"\b{re.escape(command)}\b",
            sql,
            re.IGNORECASE,
        ):
            return False

    # Validate FROM/JOIN tables.
    approved_tables = _extract_tables(sql)

    if not approved_tables:
        return False

    # Validate columns.
    if not _columns_are_allowed(
        sql,
        approved_tables,
    ):
        return False

    return True