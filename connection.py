import anthropic
import snowflake.connector
from dotenv import load_dotenv
import os

# Load credentials from .env file
load_dotenv()

# Connect to Snowflake
print("Connecting to Snowflake...")
conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)

print("✅ Snowflake connected successfully!")

# Run a simple test query
cursor = conn.cursor()
cursor.execute("SELECT CURRENT_VERSION()")
row = cursor.fetchone()
print(f"Snowflake version: {row[0]}")

# Connect to Claude
print("\nConnecting to Claude...")
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say 'Claude and Snowflake are connected!' and nothing else."}]
)

print(f"✅ Claude response: {message.content[0].text}")

# Clean up
cursor.close()
conn.close()
print("\n🎉 Connection test complete!")