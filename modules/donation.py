import streamlit as st
import pandas as pd
import mysql.connector

import pandas as pd

def show():
    st.title("🤝 Smart Donation Allocation (NGO-Based)")

    # ---------- DB Connection ----------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Wsrsid@75",
        database="smart_distribution"
    )

    query = """
    SELECT
        i.location,
        i.product_id,
        i.product_name,
        i.category,
        i.closing_stock,
        i.days_to_expiry,

        n.ngo_id,
        n.ngo_name,
        n.daily_capacity_units,

        LEAST(i.closing_stock, n.daily_capacity_units) AS units_allocated

    FROM inventory i
    JOIN ngo_master n
        ON i.location = n.location
       AND i.category = n.category_accepted
       AND i.days_to_expiry >= n.min_shelf_life_days
       AND n.active_flag = 1

    WHERE i.decision = 'DONATE'
      AND i.closing_stock > 0
    """

    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        st.warning("No donation-eligible items found for NGOs.")
        return

    # ---------- Sustainability Metrics ----------
    df["co2_saved_kg"] = df["units_allocated"] * 0.5
    df["people_served"] = df["units_allocated"] * 2

    # ---------- KPIs ----------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Units Donated", int(df["units_allocated"].sum()))
    col2.metric("NGOs Involved", df["ngo_id"].nunique())
    col3.metric("CO₂ Saved (kg)", round(df["co2_saved_kg"].sum(), 1))
    col4.metric("People Served", int(df["people_served"].sum()))

    st.markdown("---")

    # ---------- Filters ----------
    st.sidebar.header("🔍 Filters")

    ngo_filter = st.sidebar.selectbox(
        "NGO",
        ["All"] + sorted(df["ngo_name"].unique().tolist()),
        key="ngo_filter"
    )

    location_filter = st.sidebar.selectbox(
        "Location",
        ["All"] + sorted(df["location"].unique().tolist()),
        key="don_location"
    )

    filtered_df = df.copy()

    if ngo_filter != "All":
        filtered_df = filtered_df[filtered_df["ngo_name"] == ngo_filter]

    if location_filter != "All":
        filtered_df = filtered_df[filtered_df["location"] == location_filter]

    # ---------- Display ----------
    st.subheader("📦 NGO-wise Donation Allocation")

    display_df = filtered_df[[
        "ngo_name",
        "location",
        "product_name",
        "category",
        "units_allocated",
        "days_to_expiry",
        "people_served"
    ]]

    st.dataframe(display_df, width="stretch")

    # ---------- Category Impact ----------
    st.subheader("📊 Donation Units by Category")

    cat_summary = (
        filtered_df
        .groupby("category")["units_allocated"]
        .sum()
        .reset_index()
    )

    st.bar_chart(cat_summary, x="category", y="units_allocated")

    # ---------- Export ----------
    st.markdown("### ⬇ Export NGO Allocation Plan")

    csv = display_df.to_csv(index=False)

    st.download_button(
        "Download Donation Allocation CSV",
        csv,
        file_name="ngo_donation_allocation.csv",
        mime="text/csv",
        key="ngo_export"
    )



