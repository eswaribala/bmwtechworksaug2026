from bmw_analyst.snowflake.connection import get_connection

connection = get_connection(use_database=False)
cursor = connection.cursor()

cursor.execute("SHOW GRANTS TO USER ARUL")

rows = cursor.fetchall()

for row in rows:
    print(row)

cursor.close()
connection.close()
