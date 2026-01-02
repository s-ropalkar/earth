import streamlit as st
import pandas as pd
import mysql.connector


def show():
    st.title("🚨 Risk & Early Alerts")
    st.caption("Early warning system for stock-out risks")

    # ---------- MySQL Connection ----------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Wsrsid@75",
        database="smart_distribution"
    )

    query = """
    SELECT
        location,
        product_id,
        product_name,
        category,
        closing_stock,
        daily_sales_avg,
        lead_time_days,
        decision
    FROM inventory
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # ---------- Derived Metrics ----------
    df["days_cover"] = df.apply(
        lambda x: round(x["closing_stock"] / x["daily_sales_avg"], 1)
        if x["daily_sales_avg"] > 0 else 999,
        axis=1
    )

    # ---------- Risk Classification ----------
    def risk_level(row):
        if row["days_cover"] < row["lead_time_days"]:
            return "HIGH"
        elif row["days_cover"] < row["lead_time_days"] + 2:
            return "MEDIUM"
        else:
            return "SAFE"

    df["risk_level"] = df.apply(risk_level, axis=1)

    # ---------- TOP FILTERS (NOT SIDEBAR) ----------
    st.markdown("### 🔍 Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        location_filter = st.selectbox(
            "Location",
            ["All"] + sorted(df["location"].unique().tolist()),
            key="risk_location"
        )

    with col2:
        category_filter = st.selectbox(
            "Category",
            ["All"] + sorted(df["category"].unique().tolist()),
            key="risk_category"
        )

    with col3:
        risk_filter = st.selectbox(
            "Risk Level",
            ["All", "HIGH", "MEDIUM"],
            key="risk_level"
        )

    # ---------- Apply Filters ----------
    filtered_df = df.copy()

    if location_filter != "All":
        filtered_df = filtered_df[filtered_df["location"] == location_filter]

    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]

    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df["risk_level"] == risk_filter]
    else:
        filtered_df = filtered_df[filtered_df["risk_level"] != "SAFE"]

    # ---------- Sort by Priority ----------
    filtered_df = filtered_df.sort_values(
        by=["risk_level", "days_cover"],
        ascending=[True, True]
    )

    # ---------- Display ----------
    st.markdown("### 📋 Items at Risk")

    display_df = filtered_df[[
        "location",
        "product_name",
        "category",
        "days_cover",
        "lead_time_days",
        "risk_level"
    ]]

    st.dataframe(display_df, width="stretch")

    # ---------- Export ----------
    st.markdown("### ⬇ Export Procurement Priority List")

    csv_data = display_df.to_csv(index=False)

    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="procurement_priority.csv",
        mime="text/csv",
        key="risk_export"
    )
