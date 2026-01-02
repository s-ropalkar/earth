import streamlit as st
import pandas as pd
import mysql.connector


# streamlit run src/streamlit_app.py
def show():
    st.title("📦 Reorder Planning")

    st.caption(
        "This page converts stock risk signals into procurement-ready reorder quantities "
        "using lead-time based safety stock logic."
    )

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

    # ---------- Reorder Logic ----------
    # Rule:
    # If decision == REORDER and stock will not cover lead time
    df_reorder = df[
        (df["decision"] == "REORDER") &
        (df["days_cover"] < df["lead_time_days"])
    ].copy()

    # ---------- Reorder Quantity Formula ----------
    # reorder_qty = (lead_time * avg_sales * safety_factor) - current_stock
    SAFETY_FACTOR = 1.2

    df_reorder["suggested_reorder_qty"] = (
        (df_reorder["lead_time_days"] *
         df_reorder["daily_sales_avg"] *
         SAFETY_FACTOR)
        - df_reorder["closing_stock"]
    ).round(0)

    df_reorder["suggested_reorder_qty"] = df_reorder[
        "suggested_reorder_qty"
    ].apply(lambda x: max(int(x), 0))

    # ---------- Priority ----------
    def priority(row):
        if row["days_cover"] < row["lead_time_days"] - 1:
            return "HIGH"
        else:
            return "MEDIUM"

    df_reorder["priority"] = df_reorder.apply(priority, axis=1)

    # ---------- Filters (TOP, NOT SIDEBAR) ----------
    col1, col2 = st.columns(2)

    with col1:
        location_filter = st.selectbox(
            "📍 Location",
            ["All"] + sorted(df_reorder["location"].unique().tolist())
        )

    with col2:
        category_filter = st.selectbox(
            "📦 Category",
            ["All"] + sorted(df_reorder["category"].unique().tolist())
        )

    # ---------- Apply Filters ----------
    filtered_df = df_reorder.copy()

    if location_filter != "All":
        filtered_df = filtered_df[
            filtered_df["location"] == location_filter
        ]

    if category_filter != "All":
        filtered_df = filtered_df[
            filtered_df["category"] == category_filter
        ]

    # ---------- Sort ----------
    filtered_df = filtered_df.sort_values(
        by=["priority", "days_cover"],
        ascending=[True, True]
    )

    # ---------- Display ----------
    st.subheader("🧾 Suggested Reorders")

    display_df = filtered_df[[
        "location",
        "product_name",
        "category",
        "daily_sales_avg",
        "closing_stock",
        "lead_time_days",
        "suggested_reorder_qty",
        "priority"
    ]]

    st.dataframe(display_df, use_container_width=True)

    # ---------- Export ----------
    st.markdown("### ⬇ Export Reorder Plan")

    csv_data = display_df.to_csv(index=False)

    st.download_button(
        label="Download Reorder CSV",
        data=csv_data,
        file_name="reorder_plan.csv",
        mime="text/csv"
    )
