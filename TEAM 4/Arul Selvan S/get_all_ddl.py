from bmw_analyst.snowflake.connection import get_connection

connection = get_connection(use_database=False)
cursor = connection.cursor()

tables = [
    "BMW_WARRANTY",
    "BMW_FAULTS",
    "BMW_BATTERY",
]

for table in tables:
    print("\n" + "=" * 70)
    print(table)
    print("=" * 70)

    cursor.execute(f"""
        SELECT GET_DDL(
            'TABLE',
            'BMW_ANALYTICS.BMW_DATA.{table}'
        )
    """)

    print(cursor.fetchone()[0])

cursor.close()
connection.close()
