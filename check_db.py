import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
)

cursor = conn.cursor()
cursor.execute("SHOW DATABASES")
print("Available databases:")
for row in cursor.fetchall():
    print(" -", row[1])

cursor.close()
conn.close()