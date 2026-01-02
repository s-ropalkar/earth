import streamlit as st
import pandas as pd
import mysql.connector
import pandas as pd

def show():
    st.title("📈 Impact & Audit – Decision Outcomes")

    # ---------- MySQL Connection ----------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Wsrsid@75",
        database="smart_distribution"
    )

    query = """
    SELECT
        product_id,
        product_name,
        location,
        decision,
        decision_reason,
        closing_stock,
        daily_sales_avg,
        days_to_expiry
    FROM inventory
    """

    df = pd.read_sql(query, conn)
    conn.close()

    st.markdown(
        "This page evaluates the **real impact** of inventory decisions and provides an **audit trail** for governance."
    )

    # ---------- IMPACT METRICS ----------
    waste_prevented = df[df["decision"] == "DONATE"].shape[0]

    stockout_avoided = df[
        (df["decision"] == "REORDER") &
        (df["closing_stock"] < df["daily_sales_avg"] * 3)
    ].shape[0]

    healthy_items = df[df["decision"] == "OK"].shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("♻️ Waste Prevented (Units)", waste_prevented)
    col2.metric("🚫 Stock-outs Avoided", stockout_avoided)
    col3.metric("✅ Stable Inventory Items", healthy_items)

    st.markdown("---")

    # ---------- BEFORE vs AFTER (SIMULATED) ----------
    st.subheader("Before vs After – Inventory Health")

    before = {
        "Healthy": int(len(df) * 0.4),
        "At Risk": int(len(df) * 0.6)
    }

    after = {
        "Healthy": healthy_items,
        "At Risk": len(df) - healthy_items
    }

    impact_df = pd.DataFrame({
        "Status": ["Healthy", "At Risk"],
        "Before Decisions": [before["Healthy"], before["At Risk"]],
        "After Decisions": [after["Healthy"], after["At Risk"]],
    })

    st.bar_chart(
        data=impact_df.set_index("Status")
    )

    st.markdown("---")

    # ---------- AUDIT LOG ----------
    st.subheader("📜 Decision Audit Log")

    audit_df = df[[
        "product_id",
        "product_name",
        "location",
        "decision",
        "decision_reason"
    ]].sort_values(by="decision")

    st.dataframe(audit_df, width="stretch")

    # ---------- GOVERNANCE NOTE ----------
    with st.expander("🔍 Governance & Explainability"):
        st.markdown("""
**Why this audit matters:**

• Every decision is **rule-based and explainable**  
• No black-box AI decisions  
• Decisions can be reviewed by operations managers  
• Suitable for compliance, NGOs, and public sector use  

This ensures **accountability, transparency, and trust**.
        """)
