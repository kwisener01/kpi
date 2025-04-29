import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
from io import BytesIO
import plotly.express as px
from fpdf import FPDF

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
page = st.sidebar.radio("Go to", ("KPI Dashboard", "Daily CTQ Tracker", "Customer Rework Report"))

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

if page == "KPI Dashboard":
    st.title("\U0001F4CA KPI Dashboard")

    with st.form("KPI Form"):
        st.subheader("Enter KPI Data:")
        kpi_date = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", list(kpi_options.keys()))
        kpi_name = st.selectbox("KPI Name", list(kpi_options.keys()))
        default_target = kpi_options.get(kpi_name, "")
        target = st.text_input("Target Value", value=default_target)
        actual = st.text_input("Actual Value")
        notes = st.text_area("Notes/Actions")
        submit_kpi = st.form_submit_button("Submit KPI")

    if submit_kpi:
        try:
            actual_val = float(actual.replace('%','').replace('$','').replace('Units','').replace('minutes','').replace('hours','').strip())
            target_val = float(target.replace('%','').replace('$','').replace('Units','').replace('minutes','').replace('hours','').strip())
            if "<" in target:
                status = "Met" if actual_val < target_val else "Missed"
            elif ">" in target:
                status = "Met" if actual_val > target_val else "Missed"
            else:
                status = "Met" if actual_val == target_val else "Missed"
        except:
            status = "Check Data"

        new_kpi = {
            'Date': kpi_date,
            'Category': category,
            'KPI': kpi_name,
            'Target': target,
            'Actual': actual,
            'Status': status,
            'Notes/Actions': notes
        }
        kpi_data = pd.concat([kpi_data, pd.DataFrame([new_kpi])], ignore_index=True)
        kpi_data.to_csv(kpi_csv, index=False)
        st.success(f"KPI for {kpi_name} on {kpi_date} saved!")

    st.subheader("\U0001F4CB KPI Records")
    filter_category = st.selectbox("Filter by Category", options=["All"] + list(kpi_data['Category'].unique()))
    filter_month = st.selectbox("Filter by Month", options=["All"] + list(kpi_data['Date'].apply(lambda x: str(x)[:7]).unique()))

    filtered_kpi_data = kpi_data.copy()
    if filter_category != "All":
        filtered_kpi_data = filtered_kpi_data[filtered_kpi_data['Category'] == filter_category]
    if filter_month != "All":
        filtered_kpi_data = filtered_kpi_data[filtered_kpi_data['Date'].apply(lambda x: str(x)[:7]) == filter_month]

    def highlight_status(val):
        color = 'green' if val == 'Met' else 'red' if val == 'Missed' else 'gray'
        return f'background-color: {color}'

    if not filtered_kpi_data.empty:
        styled_kpi = filtered_kpi_data.style.applymap(highlight_status, subset=['Status'])
        st.dataframe(styled_kpi)

    st.subheader("\U0001F4C9 KPI Status Overview")
    if not filtered_kpi_data.empty:
        status_counts = filtered_kpi_data['Status'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90, colors=['green', 'red', 'gray'])
        ax.axis('equal')
        st.pyplot(fig)

elif page == "Daily CTQ Tracker":
    st.title("\U0001F4C8 Daily CTQ Tracker")

    with st.form("CTQ Form"):
        st.subheader("Enter Today's CTQ Data:")
        entry_date = st.date_input("Date", value=date.today())
        defect_rate = st.number_input("Daily Defect Rate (%)", min_value=0.0, max_value=100.0, value=0.0)
        fp_yield = st.number_input("First Pass Yield (%)", min_value=0.0, max_value=100.0, value=100.0)
        downtime_events = st.number_input("Downtime Events (#)", min_value=0, value=0)
        scrap_units = st.number_input("Scrap Units (#)", min_value=0, value=0)
        calibration_misses = st.number_input("Calibration Misses (#)", min_value=0, value=0)
        submit = st.form_submit_button("Submit")

    if submit:
        score = 0
        score += 1 if defect_rate < 1 else 0
        score += 1 if fp_yield >= 95 else 0
        score += 1 if downtime_events == 0 else 0
        score += 1 if scrap_units <= 2 else 0
        score += 1 if calibration_misses == 0 else 0

        if score == 5:
            recommendation = "✅ Excellent - Keep it up!"
        elif 3 <= score <= 4:
            recommendation = "⚠️ Caution - Monitor closely."
        else:
            recommendation = "❌ Immediate Action Needed!"

        new_row = {
            'Date': entry_date,
            'Daily Defect Rate (%)': defect_rate,
            'First Pass Yield (%)': fp_yield,
            'Downtime Events (#)': downtime_events,
            'Scrap Units (#)': scrap_units,
            'Calibration Misses (#)': calibration_misses,
            'Daily CTQ Health Score': score,
            'Recommendation': recommendation
        }
        ctq_data = pd.concat([ctq_data, pd.DataFrame([new_row])], ignore_index=True)
        ctq_data.to_csv(ctq_csv, index=False)
        st.success(f"Entry for {entry_date} saved!")

    st.subheader("\U0001F4C9 Recent CTQ Records")
    st.dataframe(ctq_data.tail(10))

elif page == "Customer Rework Report":
    st.title("\U0001F527 Customer Rework Report")

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

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Customer Rework Report", ln=True, align='C')

        for index, row in pareto_df.iterrows():
            if internal_view:
                line = f"{row['Discard Reason']}: {row['Count']} ({row['Percentage']}%)"
            else:
                line = f"{row['Discard Reason']}: {row['Percentage']}%"
            pdf.cell(200, 10, txt=line, ln=True, align='L')

        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)

        st.download_button(
            label="Download PDF",
            data=pdf_output,
            file_name='customer_rework_report.pdf',
            mime='application/pdf'
        )
