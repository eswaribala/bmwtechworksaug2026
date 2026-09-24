
from bmw_analyst.snowflake.executor import apply_query_limit


def test_query_limit_is_added():
    sql = """
    SELECT model
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    """

    result = apply_query_limit(sql)

    assert result.endswith("LIMIT 1000")


def test_existing_query_limit_is_preserved():
    sql = """
    SELECT model
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    LIMIT 10
    """

    result = apply_query_limit(sql)

    assert result.endswith("LIMIT 10")
    assert "LIMIT 1000" not in result


def test_query_without_limit_gets_protection():
    sql = """
    SELECT model, warranty_cost
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    ORDER BY warranty_cost DESC
    """

    result = apply_query_limit(sql)

    assert "LIMIT 1000" in result


def test_trailing_semicolon_is_removed():
    sql = """
    SELECT model
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY;
    """

    result = apply_query_limit(sql)

    assert result.endswith("LIMIT 1000")
    assert not result.endswith(";")