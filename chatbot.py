import anthropic
import os
import json
from dotenv import load_dotenv
from snowflake_connector import run_query

load_dotenv()

# Full schema context for Claude
SCHEMA_CONTEXT = """
You are a data analyst assistant. You have access to a Snowflake table with the following details:

Table: CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC

Columns:
- HOST_ID         : Unique identifier for the host
- HOST_SINCE      : Date the host joined Airbnb
- NAME            : Name/title of the listing
- NEIGHBOURHOOD   : Neighbourhood where the listing is located (e.g. Brooklyn, Manhattan, Queens)
- PROPERTY_TYPE   : Type of property (e.g. Apartment, House, Condo)
- REVIEW_SCORES_RATING_BIN : Binned review score category (e.g. 'Excellent', 'Good', etc.)
- ROOM_TYPE       : Type of room (e.g. 'Entire home/apt', 'Private room', 'Shared room')
- ZIPCODE         : ZIP code of the listing
- BEDS            : Number of beds
- NUMBER_OF_RECORDS : Number of records for this listing
- NUMBER_OF_REVIEWS : Total number of reviews
- PRICE           : Nightly price in USD (numeric)
- REVIEW_SCORES_RATING : Numeric review score (e.g. 4.5, 5.0)

Rules for generating SQL:
1. Always use the full table name: CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC
2. Always use LIMIT 100 unless the user asks for more or for aggregations
3. For price comparisons, use numeric comparisons (e.g. PRICE < 100)
4. NEIGHBOURHOOD values are mixed case - use ILIKE for text matching (e.g. NEIGHBOURHOOD ILIKE '%brooklyn%')
5. ROOM_TYPE values: 'Entire home/apt', 'Private room', 'Shared room'
6. Return only valid Snowflake SQL — no markdown, no explanation, just the SQL query
"""

def natural_language_to_sql(user_question: str) -> str:
    """Convert a natural language question to a SQL query using Claude."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SCHEMA_CONTEXT,
        messages=[
            {"role": "user", "content": f"Convert this question to SQL: {user_question}"}
        ]
    )
    sql = message.content[0].text.strip()
    # Clean up any accidental markdown code fences
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def summarize_results(user_question: str, results: list) -> str:
    """Ask Claude to summarize query results in plain English."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Limit to first 20 rows for summarization to keep tokens low
    sample = results[:20]

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": (
                    f"The user asked: '{user_question}'\n\n"
                    f"The query returned {len(results)} rows. Here is a sample:\n{json.dumps(sample, indent=2, default=str)}\n\n"
                    f"Please summarize the answer in 2-3 plain English sentences."
                )
            }
        ]
    )
    return message.content[0].text.strip()


def ask(user_question: str) -> dict:
    """
    Full pipeline: natural language → SQL → Snowflake → plain English summary.
    Returns a dict with keys: question, sql, results, summary
    """
    print(f"\n🔍 Question: {user_question}")

    # Step 1: Generate SQL
    sql = natural_language_to_sql(user_question)
    print(f"\n📝 Generated SQL:\n{sql}")

    # Step 2: Run query
    results = run_query(sql)
    print(f"\n✅ Returned {len(results)} rows")

    # Step 3: Summarize
    summary = summarize_results(user_question, results)
    print(f"\n💬 Summary: {summary}")

    return {
        "question": user_question,
        "sql": sql,
        "results": results,
        "summary": summary
    }


# ── Terminal test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_questions = [
        "What is the average price in Brooklyn?",
        "Which neighbourhood has the most listings?",
        "Show me all entire home listings under $100"
    ]

    for q in test_questions:
        print("\n" + "="*60)
        response = ask(q)
        print(f"\n📊 Results preview (first 3 rows):")
        for row in response["results"][:3]:
            print(row)
