import snowflake.connector
import pandas as pd
from dotenv import load_dotenv
import os
import math

load_dotenv()

# Load CSV
print("Reading CSV file...")
df = pd.read_csv("airbnb(AirBnB_NYC).csv", encoding="latin1")
df.columns = [c.upper().replace(" ", "_").replace("(", "").replace(")", "") for c in df.columns]
print(f"✅ Loaded {len(df)} rows")

# Clean data
print("Cleaning data...")
def clean_val(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, str):
        v = v.strip()
        if v.lower() in ('nan', 'none', ''):
            return None
        # Remove commas from numbers like 1,990
        v = v.replace(',', '')
    return v

data = [tuple(clean_val(v) for v in row) for row in df.values.tolist()]
print("✅ Data cleaned!")

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
cursor = conn.cursor()
print("✅ Connected!")

# Create table
print("Creating table...")
cursor.execute("""
    CREATE OR REPLACE TABLE AIRBNB_NYC (
        HOST_ID INTEGER,
        HOST_SINCE VARCHAR(50),
        NAME VARCHAR(500),
        NEIGHBOURHOOD VARCHAR(100),
        PROPERTY_TYPE VARCHAR(100),
        REVIEW_SCORES_RATING_BIN FLOAT,
        ROOM_TYPE VARCHAR(100),
        ZIPCODE VARCHAR(20),
        BEDS INTEGER,
        NUMBER_OF_RECORDS INTEGER,
        NUMBER_OF_REVIEWS INTEGER,
        PRICE VARCHAR(20),
        REVIEW_SCORES_RATING FLOAT
    )
""")
print("✅ Table created!")

# Insert rows
print("Inserting rows (this may take a moment)...")
insert_sql = """
    INSERT INTO AIRBNB_NYC VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""
cursor.executemany(insert_sql, data)
conn.commit()
print(f"✅ {len(df)} rows inserted into AIRBNB_NYC!")

cursor.close()
conn.close()
print("\n🎉 Ingestion complete!")