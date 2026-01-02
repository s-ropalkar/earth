import streamlit as st
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
st.set_page_config(
    page_title="ESIP – Essential Supply Intelligence Platform",
    layout="wide"
)

st.title("🧠 Essential Supply Intelligence Platform (ESIP)")
st.caption("AI-assisted decision intelligence for critical goods")

st.sidebar.title("🧭 Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "📊 Overview",
        "🚨 Risk & Alerts",
        "🗺️ Allocation Insights",
        "🤝 Donation & Redistribution",
        "📦 Reorder Planning",
        "📈 Impact & Audit"
    ]
)

if page == "📊 Overview":
    from modules.overview import show

    show()

elif page == "🚨 Risk & Alerts":
    from modules.risk_alerts import show
    show()

elif page == "🗺️ Allocation Insights":
    from modules.allocation import show
    show()

elif page == "🤝 Donation & Redistribution":
    from modules.donation import show
    show()

elif page == "📦 Reorder Planning":
    from modules.reorder import show
    show()

elif page == "📈 Impact & Audit":
    from modules.impact import show
    show()
# ngo_demand (
#     demand_id,
#     ngo_id,
#     product_id,
#     required_quantity,
#     urgency_score,         -- 1 (low) to 10 (critical)
#     needed_by_date,
#     created_date
# )