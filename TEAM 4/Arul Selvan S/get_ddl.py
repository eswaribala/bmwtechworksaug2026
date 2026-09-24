from bmw_analyst.snowflake.connection import get_connection

connection = get_connection(use_database=False)
cursor = connection.cursor()

cursor.execute("""
SELECT GET_DDL(
    'TABLE',
    'BMW_ANALYTICS.BMW_DATA.BMW_VEHICLE_SALES'
)
""")

print(cursor.fetchone()[0])

cursor.close()
connection.close()
