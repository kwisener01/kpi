import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
from io import BytesIO
import plotly.express as px
from fpdf import FPDF
import tempfile

# Initialize the CSV files
ctq_csv = 'daily_ctq_records.csv'
kpi_csv = 'kpi_records.csv'

# Load existing CTQ data if available
try:
    ctq_data = pd.read_csv(ctq_csv)
except FileNotFoundError:
    ctq_data = pd.DataFrame(columns=[
        'Date', 'Daily Defect Rate (%)', 'First Pass Yield (%)', 
        'Downtime Events (#)', 'Scrap Units (#)', 'Calibration Misses (#)', 
        'Daily CTQ Health Score', 'Recommendation'
    ])

# Load existing KPI data if available
try:
    kpi_data = pd.read_csv(kpi_csv)
except FileNotFoundError:
    kpi_data = pd.DataFrame(columns=[
        'Date', 'Category', 'KPI', 'Target', 'Actual', 'Status', 'Notes/Actions'
    ])

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("🏠 Dashboard Home", "📊 KPI Dashboard", "📈 Daily CTQ Tracker", "🛠 Customer Rework Report"))

kpi_options = {
    "First Pass Yield (%)": "95%+",
    "Retest Rate (%)": "<5%",
    "Units Tested per Shift": "120 Units",
    "Average Testing Cycle Time (min)": "<5 minutes",
    "Equipment Downtime (minutes)": "<120 minutes",
    "Mean Time to Repair (MTTR) (min)": "<30 minutes",
    "Mean Time Between Failures (MTBF) (hours)": ">100 hours",
    "Testing Cost per Unit ($)": "<$2.00",
    "Scrap/Rework Cost ($)": "<$500",
    "Root Cause Attempt Rate (%)": "90%+",
    "Corrective Action Completion Rate (%)": "95%+",
    "5S Audit Score (%)": "95%+",
    "Safety Incidents/Near Misses (#)": "0",
    "Cross-Training Rate (%)": "80%+",
    "Improvement Ideas Submitted (#)": "≥3 ideas"
}

if page == "🏠 Dashboard Home":
    st.title("🏠 Dashboard Home")
    st.write("Welcome to your Manufacturing Performance Dashboard!")

    st.subheader("Today's Quick Summary:")

    today = pd.to_datetime(date.today())
    todays_kpi = kpi_data[kpi_data['Date'] == str(today.date())]
    todays_ctq = ctq_data[ctq_data['Date'] == str(today.date())]

    st.metric("Today's KPIs Logged", len(todays_kpi))
    if not todays_ctq.empty:
        latest_ctq = todays_ctq.iloc[-1]
        st.metric("Today's CTQ Health Score", f"{latest_ctq['Daily CTQ Health Score']}/5")
    else:
        st.metric("Today's CTQ Health Score", "No Data")

    st.subheader("Quick Links:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Go to KPI Dashboard"):
            st.session_state.page = "📊 KPI Dashboard"
    with col2:
        if st.button("📈 Go to Daily CTQ Tracker"):
            st.session_state.page = "📈 Daily CTQ Tracker"
    with col3:
        if st.button("🛠 Go to Customer Rework Report"):
            st.session_state.page = "🛠 Customer Rework Report"

elif page == "📊 KPI Dashboard":
    # KPI Dashboard code (your existing)
    pass

elif page == "📈 Daily CTQ Tracker":
    # Daily CTQ Tracker code (your existing)
    pass

elif page == "🛠 Customer Rework Report":
    # Customer Rework Report code (your existing)
    pass
