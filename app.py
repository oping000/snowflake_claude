import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from chatbot import ask
from snowflake_connector import run_query

st.set_page_config(page_title="Airbnb NYC Analytics", page_icon="\U0001f3d9\ufe0f", layout="wide")

st.markdown("""
    <style>
        .sql-box { background-color: #1e1e1e; color: #d4d4d4; padding: 12px 16px; border-radius: 8px; font-family: Courier New, monospace; font-size: 13px; margin: 8px 0; }
        .summary-box { background-color: #e8f4f8; border-left: 4px solid #0ea5e9; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }
        .insight-box { background-color: #f0fdf4; border-left: 4px solid #22c55e; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }
        .ab-result-box { background-color: #fefce8; border-left: 4px solid #eab308; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Dataset Info")
    st.markdown("- **Source:** Airbnb NYC\n- **Rows:** 30,478\n- **Database:** CLAUDE_PROJECTS\n- **Schema:** AIRBNB\n- **Table:** AIRBNB_NYC")
    st.divider()
    st.markdown("### Sample Questions")
    st.markdown("- What is the average price in Manhattan?\n- How many private rooms are under $75?\n- Which zipcode has the highest rated listings?\n- Show me listings with more than 100 reviews\n- What is the most common property type?")
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

st.title("Airbnb NYC - AI Analytics Assistant")
st.markdown("Powered by **Claude AI** + **Snowflake**")
st.divider()

tab1, tab2, tab3 = st.tabs(["AI Chatbot", "Insights Dashboard", "A/B Testing"])

with tab1:
    st.markdown("### Ask anything about the Airbnb NYC data")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Average price in Brooklyn?"):
            st.session_state.prefill = "What is the average price in Brooklyn?"
    with col2:
        if st.button("Most listings by neighbourhood?"):
            st.session_state.prefill = "Which neighbourhood has the most listings?"
    with col3:
        if st.button("Entire homes under $100?"):
            st.session_state.prefill = "Show me all entire home listings under $100"
    st.divider()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                st.markdown(f'<div class="summary-box">{msg["summary"]}</div>', unsafe_allow_html=True)
                with st.expander("View SQL Query"):
                    st.markdown(f'<div class="sql-box">{msg["sql"]}</div>', unsafe_allow_html=True)
                if msg["results"]:
                    with st.expander(f'View Data ({len(msg["results"])} rows)'):
                        st.dataframe(pd.DataFrame(msg["results"]), use_container_width=True)
            else:
                st.markdown(msg["content"])

    prefill = st.session_state.pop("prefill", "")
    user_input = st.chat_input("Ask anything about the Airbnb NYC data...")
    question = prefill or user_input

    if question:
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("assistant"):
            with st.spinner("Thinking... querying Snowflake..."):
                try:
                    response = ask(question)
                    st.markdown(f'<div class="summary-box">{response["summary"]}</div>', unsafe_allow_html=True)
                    with st.expander("View SQL Query"):
                        st.markdown(f'<div class="sql-box">{response["sql"]}</div>', unsafe_allow_html=True)
                    if response["results"]:
                        with st.expander(f'View Data ({len(response["results"])} rows)'):
                            st.dataframe(pd.DataFrame(response["results"]), use_container_width=True)
                    st.session_state.messages.append({"role": "assistant", "summary": response["summary"], "sql": response["sql"], "results": response["results"]})
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab2:
    st.markdown("### Airbnb NYC - Insights Dashboard")
    with st.spinner("Loading dashboard data from Snowflake..."):
        try:
            metrics = run_query("SELECT COUNT(*) AS TOTAL_LISTINGS, ROUND(AVG(PRICE),2) AS AVG_PRICE, MIN(PRICE) AS MIN_PRICE, MAX(PRICE) AS MAX_PRICE, COUNT(DISTINCT NEIGHBOURHOOD) AS TOTAL_NEIGHBOURHOODS FROM CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC")
            m = metrics[0]
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Total Listings", f'{m["TOTAL_LISTINGS"]:,}')
            c2.metric("Avg Price", f'${m["AVG_PRICE"]}')
            c3.metric("Min Price", f'${m["MIN_PRICE"]}')
            c4.metric("Max Price", f'${m["MAX_PRICE"]}')
            c5.metric("Neighbourhoods", m["TOTAL_NEIGHBOURHOODS"])
            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Average Price by Neighbourhood (Top 15)")
                d = run_query("SELECT NEIGHBOURHOOD, ROUND(AVG(PRICE),2) AS AVG_PRICE FROM CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC WHERE NEIGHBOURHOOD IS NOT NULL GROUP BY NEIGHBOURHOOD ORDER BY AVG_PRICE DESC LIMIT 15")
                df = pd.DataFrame(d)
                fig = px.bar(df, x="AVG_PRICE", y="NEIGHBOURHOOD", orientation="h", color="AVG_PRICE", color_continuous_scale="Oranges")
                fig.update_layout(height=450, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown("#### Listings by Room Type")
                d = run_query("SELECT ROOM_TYPE, COUNT(*) AS COUNT FROM CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC WHERE ROOM_TYPE IS NOT NULL GROUP BY ROOM_TYPE ORDER BY COUNT DESC")
                df = pd.DataFrame(d)
                fig = px.pie(df, names="ROOM_TYPE", values="COUNT", color_discrete_sequence=px.colors.qualitative.Set2, hole=0.4)
                fig.update_layout(height=450)
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            col3, col4 = st.columns(2)
            with col3:
                st.markdown("#### Top 10 Neighbourhoods by Listings")
                d = run_query("SELECT NEIGHBOURHOOD, COUNT(*) AS TOTAL_LISTINGS FROM CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC WHERE NEIGHBOURHOOD IS NOT NULL GROUP BY NEIGHBOURHOOD ORDER BY TOTAL_LISTINGS DESC LIMIT 10")
                df = pd.DataFrame(d)
                fig = px.bar(df, x="NEIGHBOURHOOD", y="TOTAL_LISTINGS", color="TOTAL_LISTINGS", color_continuous_scale="Blues")
                fig.update_layout(height=400, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            with col4:
                st.markdown("#### Price Distribution (Under $500)")
                d = run_query("SELECT PRICE FROM CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC WHERE PRICE IS NOT NULL AND PRICE < 500")
                df = pd.DataFrame(d)
                fig = px.histogram(df, x="PRICE", nbins=50, color_discrete_sequence=["#FF5A5F"])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.markdown("#### Average Price by Room Type")
            d = run_query("SELECT ROOM_TYPE, ROUND(AVG(PRICE),2) AS AVG_PRICE FROM CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC WHERE ROOM_TYPE IS NOT NULL GROUP BY ROOM_TYPE ORDER BY AVG_PRICE DESC")
            df = pd.DataFrame(d)
            fig = px.bar(df, x="ROOM_TYPE", y="AVG_PRICE", color="ROOM_TYPE", color_discrete_sequence=px.colors.qualitative.Pastel, text="AVG_PRICE")
            fig.update_traces(texttemplate="$%{text}", textposition="outside")
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading dashboard: {str(e)}")

with tab3:
    st.markdown("### A/B Testing - Compare Groups")
    st.markdown("Select two groups to compare. We will run a statistical significance test and explain the results in plain English.")
    compare_type = st.radio("What would you like to compare?", ["Two Neighbourhoods", "Two Room Types"], horizontal=True)
    st.divider()

    try:
        if compare_type == "Two Neighbourhoods":
            hoods = run_query("SELECT DISTINCT NEIGHBOURHOOD FROM CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC WHERE NEIGHBOURHOOD IS NOT NULL ORDER BY NEIGHBOURHOOD")
            options = [r["NEIGHBOURHOOD"] for r in hoods]
            filter_col = "NEIGHBOURHOOD"
            default_a = options.index("Manhattan") if "Manhattan" in options else 0
            default_b = options.index("Brooklyn") if "Brooklyn" in options else 1
        else:
            rooms = run_query("SELECT DISTINCT ROOM_TYPE FROM CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC WHERE ROOM_TYPE IS NOT NULL ORDER BY ROOM_TYPE")
            options = [r["ROOM_TYPE"] for r in rooms]
            filter_col = "ROOM_TYPE"
            default_a, default_b = 0, 1

        col1, col2 = st.columns(2)
        with col1:
            group_a = st.selectbox("Group A", options, index=default_a)
        with col2:
            group_b = st.selectbox("Group B", options, index=default_b)

        metric = st.selectbox("Metric to compare", ["PRICE", "REVIEW_SCORES_RATING", "NUMBER_OF_REVIEWS", "BEDS"])

        if st.button("Run A/B Test", type="primary"):
            if group_a == group_b:
                st.warning("Please select two different groups!")
            else:
                with st.spinner("Running statistical analysis..."):
                    da = run_query(f"SELECT {metric} AS VALUE FROM CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC WHERE {filter_col} ILIKE '%{group_a}%' AND {metric} IS NOT NULL")
                    db = run_query(f"SELECT {metric} AS VALUE FROM CLAUDE_PROJECTS.AIRBNB.AIRBNB_NYC WHERE {filter_col} ILIKE '%{group_b}%' AND {metric} IS NOT NULL")
                    va = [float(r["VALUE"]) for r in da if r["VALUE"] is not None]
                    vb = [float(r["VALUE"]) for r in db if r["VALUE"] is not None]
                    avg_a = round(sum(va)/len(va), 2)
                    avg_b = round(sum(vb)/len(vb), 2)
                    diff = round(avg_a - avg_b, 2)
                    pct = round((diff/avg_b)*100, 1) if avg_b != 0 else 0
                    t_stat, p_value = stats.ttest_ind(va, vb)
                    sig = p_value < 0.05

                    c1,c2,c3,c4 = st.columns(4)
                    c1.metric(f"{group_a} Avg", f"{avg_a:,}")
                    c2.metric(f"{group_b} Avg", f"{avg_b:,}")
                    c3.metric("Difference", f"{diff:+,}")
                    c4.metric("p-value", f"{p_value:.4f}")
                    st.divider()

                    if sig:
                        st.markdown(f'<div class="insight-box"><b>Statistically significant!</b> {group_a} averages <b>{avg_a:,}</b> vs {group_b} at <b>{avg_b:,}</b> — a <b>{abs(pct)}%</b> difference. (p={p_value:.4f}, not due to chance)</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="ab-result-box"><b>No significant difference found.</b> {group_a} averages <b>{avg_a:,}</b> vs {group_b} at <b>{avg_b:,}</b>. (p={p_value:.4f}, could be due to chance)</div>', unsafe_allow_html=True)

                    st.divider()
                    st.markdown("#### Distribution Comparison")
                    df_box = pd.DataFrame({"Value": va+vb, "Group": [group_a]*len(va)+[group_b]*len(vb)})
                    cap = df_box["Value"].quantile(0.99)
                    df_box = df_box[df_box["Value"] <= cap]
                    fig = px.box(df_box, x="Group", y="Value", color="Group", color_discrete_sequence=["#FF5A5F","#00A699"], points="outliers")
                    fig.update_layout(height=450, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("#### Average Comparison")
                    fig2 = go.Figure(data=[go.Bar(name=group_a, x=[group_a], y=[avg_a], marker_color="#FF5A5F"), go.Bar(name=group_b, x=[group_b], y=[avg_b], marker_color="#00A699")])
                    fig2.update_layout(height=350, showlegend=False, yaxis_title=metric.replace("_"," ").title())
                    st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Error in A/B Testing: {str(e)}")
