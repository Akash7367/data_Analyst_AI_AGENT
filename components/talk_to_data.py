import streamlit as st

def render_talk_to_data(df, filtered_df, client, date_from, date_to, sel_cat, sel_prod):
    st.markdown("### 💬 Talk-to-Data")
    st.markdown('<div class="info-box">Ask any business question in plain English. The AI will query the data and explain the answer.</div>', unsafe_allow_html=True)

    # Session state for chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "conversation_messages" not in st.session_state:
        st.session_state.conversation_messages = []

    # Quick prompts
    st.markdown("**Quick Questions:**")
    qcols = st.columns(4)
    quick_qs = [
        "What is total revenue for last 14 days?",
        "Show revenue trend for Kitchen category",
        "When did revenue drop the most?",
        "Which product has the highest avg rating?",
        "What is the avg discount by category?",
        "Which day had peak sales?",
        "Top 3 products by sales volume?",
        "Compare revenue: Electronics vs Sports"
    ]
    for i, q in enumerate(quick_qs):
        col = qcols[i % 4]
        if col.button(q, key=f"quick_{i}"):
            st.session_state["pending_query"] = q

    st.markdown("---")

    # Display chat
    chat_container = st.container()
    with chat_container:
        for entry in st.session_state.chat_history:
            if entry["role"] == "user":
                st.markdown(f'<div class="chat-user">🧑 {entry["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">🤖 {entry["content"]}</div>', unsafe_allow_html=True)

    # Input
    user_query = st.chat_input("Ask a question about your KPI data...")
    pending_query = st.session_state.pop("pending_query", None)
    
    active_query = pending_query or user_query

    if active_query and active_query.strip():
        # Build data summary for context
        data_summary = f"""
Dataset: kpi_data.csv
Shape: {df.shape[0]} rows × {df.shape[1]} columns
Date range: {df['Date'].min().date()} to {df['Date'].max().date()}
Columns: {list(df.columns)}
Categories: {df['Category'].unique().tolist()}
Products: {df['Product_Name'].unique().tolist()}

Current filtered data summary (date: {date_from} to {date_to}, category: {sel_cat}, product: {sel_prod}):
{filtered_df.describe().to_string()}

Sample rows:
{filtered_df.head(5).to_string()}

Aggregated daily revenue (last 14 days of filter):
{filtered_df.groupby('Date')['Revenue_d'].sum().tail(14).to_string()}

Revenue by category:
{filtered_df.groupby('Category')['Revenue_d'].sum().to_string()}

Revenue by product:
{filtered_df.groupby('Product_Name')['Revenue_d'].sum().sort_values(ascending=False).to_string()}

Top daily drops (day-over-day revenue change):
{filtered_df.groupby('Date')['Revenue_d'].sum().diff().nsmallest(5).to_string()}
"""

        system_prompt = f"""You are a KPI Intelligence Analyst for a retail/ecommerce business. 
You have access to the following business data:

{data_summary}

Answer the user's question with:
1. A direct, clear answer with exact numbers
2. A brief business insight or implication
3. If relevant, mention trends, anomalies, or comparisons

Use ₹ for currency values. Format numbers with commas. Be concise and executive-ready.
Do NOT use code blocks or technical jargon. Speak in plain business language."""

        st.session_state.conversation_messages.append({"role": "user", "content": active_query})

        with st.spinner("Analysing data..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.conversation_messages
                ]
            )
            answer = response.choices[0].message.content
            st.session_state.conversation_messages.append({"role": "assistant", "content": answer})

        st.session_state.chat_history.append({"role": "user",      "content": active_query})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.button("Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.session_state.conversation_messages = []
        st.rerun()
