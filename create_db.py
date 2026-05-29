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

cursor.execute("CREATE DATABASE IF NOT EXISTS CLAUDE_PROJECTS")
print("✅ Database CLAUDE_PROJECTS created!")

cursor.execute("CREATE SCHEMA IF NOT EXISTS CLAUDE_PROJECTS.AIRBNB")
print("✅ Schema AIRBNB created!")

cursor.close()
conn.close()