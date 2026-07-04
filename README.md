# 🏔️ Snowflake + Claude AI Analytics Platform

## Overview
A Python-based analytics platform that integrates **Snowflake** as the data warehouse with **Claude AI** for natural language querying and **Streamlit** for interactive dashboards. Built using the Airbnb NYC dataset.

## Features
- **Snowflake Integration** — Python connector to Snowflake data warehouse
- **Claude AI Chatbot** — Natural language to SQL querying powered by Claude API
- **Incremental Data Load** — Smart CSV ingestion that only loads new rows
- **Streamlit Dashboard** — Interactive UI with multiple analytics tabs
- **A/B Testing Analytics** — Built-in analysis capabilities

## Architecture
CSV Data → Python Ingestion Script → Snowflake
↓
Claude AI API
↓
Streamlit UI (localhost:8501)

## Tech Stack
- **Python** 3.14
- **Snowflake** — Cloud data warehouse
- **Anthropic Claude API** — AI-powered natural language processing
- **Streamlit** — Interactive web dashboard
- **Pandas** — Data manipulation

## Project Structure
snowflake_claude/
├── app.py                 # Streamlit dashboard (3 tabs)
├── chatbot.py             # NL → SQL → Snowflake chatbot
├── connection.py          # Snowflake + Claude connection test
├── snowflake_connector.py # Core Snowflake connector
├── ingest_snowflake.py    # CSV ingestion script
├── incremental_load.py    # Incremental data load logic
├── create_db.py           # Database/schema creation
├── check_db.py            # Database verification utilities
├── requirements.txt       # Python dependencies
└── .gitignore             # Excludes .env and sensitive files
## Setup

### Prerequisites
- Python 3.10+
- Snowflake account
- Anthropic API key

### Installation
```bash
pip install anthropic snowflake-connector-python python-dotenv streamlit pandas
```

### Configuration
Create a `.env` file in the project root:
ANTHROPIC_API_KEY=your_api_key_here
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
### Running the App
```bash
# Test connection
python connection.py

# Load data into Snowflake
python ingest_snowflake.py

# Run incremental load (new rows only)
python incremental_load.py

# Launch Streamlit dashboard
py -m streamlit run app.py
```

## How the Incremental Load Works
1. Reads the CSV file
2. Connects to Snowflake and pulls existing records
3. Compares CSV rows against existing Snowflake rows
4. Only inserts rows that don't already exist
5. Logs all activity to `airbnb_load.log`

## How the Chatbot Works
- User types a natural language question
- Claude AI converts it to SQL
- SQL runs against Snowflake
- Results returned and displayed in Streamlit

## License
This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

© 2026 oping000 (ODell)


