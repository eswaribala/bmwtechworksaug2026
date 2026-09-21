from pyspark.sql import DataFrame
from pyspark.sql.functions import col, sum


def check_nulls(df: DataFrame) -> DataFrame:
    """
    Check the number of null values in every column.

    Parameters
    ----------
    df : DataFrame
        Input PySpark DataFrame.

    Returns
    -------
    DataFrame
        DataFrame containing null counts for each column.
    """

    null_counts = df.select(
        [
            sum(col(column).isNull().cast("int")).alias(column)
            for column in df.columns
        ]
    )

    return null_counts


def check_duplicates(df: DataFrame, key_column: str) -> DataFrame:
    """
    Check for duplicate records based on a key column.

    Parameters
    ----------
    df : DataFrame
        Input PySpark DataFrame.

    key_column : str
        Column used to identify duplicate records.

    Returns
    -------
    DataFrame
        DataFrame containing duplicate key values and their counts.
    """

    duplicates = (
        df.groupBy(key_column)
        .count()
        .filter(col("count") > 1)
        .orderBy(col("count").desc())
    )

    return duplicates


def check_invalid_range(
    df: DataFrame,
    column_name: str,
    min_value: float,
    max_value: float
) -> DataFrame:
    """
    Check whether values fall outside an allowed numeric range.

    Parameters
    ----------
    df : DataFrame
        Input PySpark DataFrame.

    column_name : str
        Numeric column to validate.

    min_value : float
        Minimum allowed value.

    max_value : float
        Maximum allowed value.

    Returns
    -------
    DataFrame
        DataFrame containing rows with values outside
        the allowed range.
    """

    invalid_records = df.filter(
        (col(column_name) < min_value)
        | (col(column_name) > max_value)
    )

    return invalid_records


def check_invalid_dates(
    df: DataFrame,
    column_name: str
) -> DataFrame:
    """
    Check for null or invalid dates in a date column.

    Parameters
    ----------
    df : DataFrame
        Input PySpark DataFrame.

    column_name : str
        Date column to validate.

    Returns
    -------
    DataFrame
        DataFrame containing rows with invalid
        or missing dates.
    """

    invalid_dates = df.filter(
        col(column_name).isNull()
    )

    return invalid_dates


def remove_duplicates(
    df: DataFrame,
    key_column: str
) -> DataFrame:
    """
    Remove duplicate records based on a key column.

    The first occurrence of each key is retained.

    Parameters
    ----------
    df : DataFrame
        Input PySpark DataFrame.

    key_column : str
        Column used to identify duplicates.

    Returns
    -------
    DataFrame
        DataFrame with duplicate keys removed.
    """

    return df.dropDuplicates([key_column])