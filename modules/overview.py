import streamlit as st
import pandas as pd
import mysql.connector
import pandas as pd


def show():
    st.title("📊 Overview – Network Health")

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
        decision,
        closing_stock,
        daily_sales_avg,
        days_to_expiry
    FROM inventory
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # ---------- KPIs ----------
    total_locations = df["location"].nunique()
    total_skus = df["product_id"].nunique()

    at_risk = df[df["decision"] != "OK"]["product_id"].nunique()
    percent_at_risk = round((at_risk / total_skus) * 100, 2)

    waste_risk_units = df[
        (df["decision"] == "DONATE") | (df["days_to_expiry"] <= 2)
    ].shape[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Locations", total_locations)
    col2.metric("Total SKUs", total_skus)
    col3.metric("% SKUs at Risk", f"{percent_at_risk}%")
    col4.metric("Units at Risk of Waste", waste_risk_units)

    st.markdown("---")

    # ---------- Stock Health Distribution ----------
    st.subheader("Stock Health Distribution")

    def classify(row):
        if row["decision"] == "OK":
            return "Healthy"
        elif row["decision"] == "REORDER" or row["closing_stock"] < row["daily_sales_avg"]:
            return "Stock-out Risk"
        else:
            return "Expiry Risk"

    df["health_status"] = df.apply(classify, axis=1)

    health_dist = df["health_status"].value_counts().reset_index()
    health_dist.columns = ["Status", "Count"]

    # ---------- Bar Chart ----------
    st.bar_chart(
        data=health_dist,
        x="Status",
        y="Count"
    )

    # ---------- Debug Table (optional) ----------
    st.write("DEBUG: Health distribution data")
    st.dataframe(health_dist)
