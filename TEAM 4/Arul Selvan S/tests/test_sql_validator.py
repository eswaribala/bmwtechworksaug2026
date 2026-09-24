from bmw_analyst.security.sql_validator import validate_sql


# ============================================================
# VALID SQL
# ============================================================

def test_valid_select():
    sql = """
    SELECT
        model,
        SUM(sales_amount) AS total_sales
    FROM BMW_VEHICLE_SALES
    GROUP BY model
    """

    assert validate_sql(sql) is True


def test_valid_fully_qualified_select():
    sql = """
    SELECT
        vehicle_id,
        model,
        city,
        warranty_cost
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    """

    assert validate_sql(sql) is True


def test_valid_count():
    sql = """
    SELECT
        fault_type,
        severity,
        COUNT(*) AS fault_count
    FROM BMW_ANALYTICS.BMW_DATA.BMW_FAULTS
    GROUP BY fault_type, severity
    ORDER BY fault_count DESC
    """

    assert validate_sql(sql) is True


def test_valid_where():
    sql = """
    SELECT
        model,
        warranty_cost
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    WHERE city = 'Chennai'
    """

    assert validate_sql(sql) is True


def test_valid_max():
    sql = """
    SELECT
        model,
        MAX(warranty_cost) AS highest_warranty_cost
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    WHERE city = 'Chennai'
    GROUP BY model
    ORDER BY highest_warranty_cost DESC
    LIMIT 1
    """

    assert validate_sql(sql) is True


def test_valid_trailing_semicolon():
    sql = """
    SELECT
        model
    FROM BMW_ANALYTICS.BMW_DATA.BMW_VEHICLE_SALES;
    """

    assert validate_sql(sql) is True


def test_valid_battery_query():
    sql = """
    SELECT
        vehicle_id,
        model,
        city,
        battery_percentage,
        battery_status
    FROM BMW_ANALYTICS.BMW_DATA.BMW_BATTERY
    WHERE city = 'Chennai'
    """

    assert validate_sql(sql) is True


# ============================================================
# INVALID / SECURITY SQL
# ============================================================

def test_reject_empty_sql():
    assert validate_sql("") is False


def test_reject_insert():
    sql = """
    INSERT INTO BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    (vehicle_id, model)
    VALUES (1, 'BMW X5')
    """

    assert validate_sql(sql) is False


def test_reject_update():
    sql = """
    UPDATE BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    SET warranty_cost = 0
    """

    assert validate_sql(sql) is False


def test_reject_delete():
    sql = """
    DELETE FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    """

    assert validate_sql(sql) is False


def test_reject_drop():
    sql = """
    DROP TABLE BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    """

    assert validate_sql(sql) is False


def test_reject_alter():
    sql = """
    ALTER TABLE BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    ADD COLUMN test_column VARCHAR
    """

    assert validate_sql(sql) is False


def test_reject_create():
    sql = """
    CREATE TABLE BMW_ANALYTICS.BMW_DATA.TEST_TABLE
    (
        ID INT
    )
    """

    assert validate_sql(sql) is False


def test_reject_truncate():
    sql = """
    TRUNCATE TABLE BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    """

    assert validate_sql(sql) is False


def test_reject_merge():
    sql = """
    MERGE INTO BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    USING BMW_ANALYTICS.BMW_DATA.BMW_VEHICLE_SALES
    ON BMW_WARRANTY.VEHICLE_ID = BMW_VEHICLE_SALES.VEHICLE_ID
    WHEN MATCHED THEN UPDATE SET warranty_cost = 0
    """

    assert validate_sql(sql) is False


def test_reject_grant():
    sql = """
    GRANT SELECT
    ON TABLE BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    TO ROLE PUBLIC
    """

    assert validate_sql(sql) is False


def test_reject_revoke():
    sql = """
    REVOKE SELECT
    ON TABLE BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    FROM ROLE PUBLIC
    """

    assert validate_sql(sql) is False


def test_reject_call():
    sql = """
    SELECT CALL('dangerous_procedure')
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    """

    assert validate_sql(sql) is False


# ============================================================
# TABLE SECURITY
# ============================================================

def test_reject_unknown_table():
    sql = """
    SELECT model
    FROM BMW_ANALYTICS.BMW_DATA.UNKNOWN_TABLE
    """

    assert validate_sql(sql) is False


def test_reject_other_database():
    sql = """
    SELECT model
    FROM OTHER_DATABASE.BMW_DATA.BMW_WARRANTY
    """

    assert validate_sql(sql) is False


def test_reject_other_schema():
    sql = """
    SELECT model
    FROM BMW_ANALYTICS.OTHER_SCHEMA.BMW_WARRANTY
    """

    assert validate_sql(sql) is False


def test_reject_unapproved_table():
    sql = """
    SELECT model
    FROM INFORMATION_SCHEMA.TABLES
    """

    assert validate_sql(sql) is False


# ============================================================
# COLUMN SECURITY
# ============================================================

def test_reject_unknown_column():
    sql = """
    SELECT secret_column
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    """

    assert validate_sql(sql) is False


def test_reject_fake_column():
    sql = """
    SELECT password
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    """

    assert validate_sql(sql) is False


# ============================================================
# STATEMENT SECURITY
# ============================================================

def test_reject_multiple_statements():
    sql = """
    SELECT model
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY;

    DROP TABLE BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
    """

    assert validate_sql(sql) is False


def test_reject_non_select():
    sql = """
    SHOW TABLES
    """

    assert validate_sql(sql) is False


def test_reject_use():
    sql = """
    SELECT model
    FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY;

    USE DATABASE OTHER_DATABASE
    """

    assert validate_sql(sql) is False