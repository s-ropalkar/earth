import streamlit as st
import pandas as pd
import mysql.connector


def show():
    st.title("📦 Allocation – Stock Rebalancing")

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
        days_to_expiry
    FROM inventory
    """

    df = pd.read_sql(query, conn)
    conn.close()

    st.markdown("This page identifies **safe stock transfers** between locations based on demand.")

    # ---------- Classification Logic ----------
    def classify_location(row):
        if row["closing_stock"] > row["daily_sales_avg"] * 7:
            return "SURPLUS"
        elif row["closing_stock"] < row["daily_sales_avg"] * 3:
            return "DEFICIT"
        else:
            return "NORMAL"

    df["stock_status"] = df.apply(classify_location, axis=1)

    # ---------- Filter Safe-to-Move Stock ----------
    safe_stock = df[df["days_to_expiry"] > 3]

    surplus_df = safe_stock[safe_stock["stock_status"] == "SURPLUS"]
    deficit_df = safe_stock[safe_stock["stock_status"] == "DEFICIT"]

    # ---------- Allocation Logic ----------
    allocations = []

    for _, surplus in surplus_df.iterrows():
        matching_deficits = deficit_df[
            (deficit_df["product_id"] == surplus["product_id"]) &
            (deficit_df["location"] != surplus["location"])
        ]

        for _, deficit in matching_deficits.iterrows():
            transfer_qty = min(
                surplus["closing_stock"] - surplus["daily_sales_avg"] * 7,
                deficit["daily_sales_avg"] * 3 - deficit["closing_stock"]
            )

            if transfer_qty > 0:
                allocations.append({
                    "Product ID": surplus["product_id"],
                    "Product Name": surplus["product_name"],
                    "Category": surplus["category"],
                    "From Location": surplus["location"],
                    "To Location": deficit["location"],
                    "Transfer Qty (Units)": int(transfer_qty),
                    "Days to Expiry": surplus["days_to_expiry"]
                })

    allocation_df = pd.DataFrame(allocations)

    # ---------- UI ----------
    st.subheader("📊 Suggested Allocations")

    if allocation_df.empty:
        st.info("No safe allocation opportunities found.")
    else:
        st.dataframe(allocation_df, width="stretch")

        # ---------- Export ----------
        csv = allocation_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Export Allocation Plan (CSV)",
            data=csv,
            file_name="allocation_plan.csv",
            mime="text/csv"
        )

    # ---------- Explanation ----------
    with st.expander("🧠 Allocation Logic Explanation"):
        st.markdown("""
**This allocation logic works as follows:**

• A location is **SURPLUS** if it has more than **7 days of stock**  
• A location is **DEFICIT** if it has less than **3 days of stock**  
• Stock is moved **only if expiry is more than 3 days away**  
• Transfers occur **only between different locations**  
• No price, distance, or NGO logic is used here (intentionally)

This ensures:
✔ Stock-outs are prevented  
✔ Expiry risk is reduced  
✔ No unsafe transfers  
✔ Logic remains explainable in interviews
        """)
