import snowflake.connector
import pandas as pd
from dotenv import load_dotenv
import os
import math
import logging
from datetime import datetime

# Setup logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "airbnb_load.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log(msg):
    print(msg)
    logging.info(msg)

# Load .env from same folder as script
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)

def clean_val(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, str):
        v = v.strip()
        if v.lower() in ('nan', 'none', ''):
            return None
        v = v.replace(',', '')
    return v

try:
    # Load CSV
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "airbnb(AirBnB_NYC).csv")
    log(f"Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path, encoding="latin1")
    df.columns = [c.upper().replace(" ", "_").replace("(", "").replace(")", "") for c in df.columns]
    log(f"✅ Loaded {len(df)} rows from CSV")

    # Connect to Snowflake
    log("Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
    cursor = conn.cursor()
    log("✅ Connected to Snowflake!")

    # Get existing keys from Snowflake
    log("Fetching existing records from Snowflake...")
    cursor.execute("SELECT HOST_ID, NAME FROM AIRBNB_NYC")
    existing = set((str(row[0]), str(row[1])) for row in cursor.fetchall())
    log(f"✅ Found {len(existing)} existing rows in Snowflake")

    # Filter only new rows
    new_rows = []
    for row in df.values.tolist():
        cleaned = tuple(clean_val(v) for v in row)
        key = (str(cleaned[0]), str(cleaned[2]))  # HOST_ID, NAME
        if key not in existing:
            new_rows.append(cleaned)

    log(f"✅ Found {len(new_rows)} new rows to insert")

    if new_rows:
        insert_sql = "INSERT INTO AIRBNB_NYC VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.executemany(insert_sql, new_rows)
        conn.commit()
        log(f"🎉 Successfully inserted {len(new_rows)} new rows!")
    else:
        log("ℹ️ No new rows to insert — table is already up to date!")

    cursor.close()
    conn.close()

except Exception as e:
    log(f"❌ Error: {str(e)}")
    raise