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
    st.page_link("#📊-kpi-dashboard", label="📊 Go to KPI Dashboard")
    st.page_link("#📈-daily-ctq-tracker", label="📈 Go to Daily CTQ Tracker")
    st.page_link("#🛠-customer-rework-report", label="🛠 Go to Customer Rework Report")

elif page == "📊 KPI Dashboard":
    # KPI Dashboard code (your existing)
    pass

elif page == "📈 Daily CTQ Tracker":
    # Daily CTQ Tracker code (your existing)
    pass

elif page == "🛠 Customer Rework Report":
    st.title("🛠 Customer Rework Report")

    rework_file = st.file_uploader("📂 Upload Rework Data CSV", type="csv", key="rework_upload")
    internal_view = st.toggle("Internal View (show counts)", value=True)
    show_ppm = st.checkbox("Show as PPM instead of %")

    if rework_file is not None:
        df = pd.read_csv(rework_file)
        df.columns = df.columns.str.strip()
        df['Discard reason'] = df['Discard reason'].fillna("Unknown")
        df['Rework Date'] = pd.to_datetime(df['Rework Date'], errors='coerce')

        min_date = df['Rework Date'].min().date()
        max_date = df['Rework Date'].max().date()
        start_date, end_date = st.date_input("📅 Select Date Range", [min_date, max_date])

        df = df[(df['Rework Date'].dt.date >= start_date) & (df['Rework Date'].dt.date <= end_date)]

        discard_counts = df['Discard reason'].value_counts()
        total_defects = discard_counts.sum()
        discard_percentage = (discard_counts / total_defects * 100).round(2)
        discard_ppm = (discard_counts / total_defects * 1_000_000).round(0)

        pareto_df = pd.DataFrame({
            'Discard Reason': discard_counts.index,
            'Count': discard_counts.values,
            'Percentage': discard_percentage.values,
            'PPM': discard_ppm.values
        })

        if not internal_view:
            pareto_df = pareto_df[['Discard Reason', 'Percentage']]

        st.subheader("📊 Rework Pareto Chart")

        if show_ppm and internal_view:
            fig = px.bar(pareto_df, x='Discard Reason', y='PPM', text='PPM')
        else:
            fig = px.bar(pareto_df, x='Discard Reason', y='Percentage', text='Percentage')

        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig)

        st.subheader("🔢 Running Total Defects (Internal)")
        if internal_view:
            st.metric(label="Total Defects", value=total_defects)

        st.subheader("📥 Download Customer Report")

        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Customer Report")
            output.seek(0)
            return output

        excel_data = convert_df_to_excel(pareto_df)
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name='customer_rework_report.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # Save Pareto chart image to temporary file
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        fig.write_image(tmpfile.name)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Customer Rework Report", ln=True, align='C')
        pdf.image(tmpfile.name, x=10, y=30, w=180)

        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)

        st.download_button(
            label="Download PDF",
            data=pdf_output,
            file_name='customer_rework_report.pdf',
            mime='application/pdf'
        )
