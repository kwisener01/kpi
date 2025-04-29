import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

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
page = st.sidebar.radio("Go to", ("KPI Dashboard", "Daily CTQ Tracker"))

if page == "KPI Dashboard":
    st.title("\U0001F4CA KPI Dashboard")

    # Form for KPI input
    with st.form("KPI Form"):
        st.subheader("Enter KPI Data:")
        kpi_date = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", ["Quality", "Efficiency", "Downtime", "Cost", "Problem Solving", "Safety/5S", "Employee Engagement"])
        kpi_name = st.text_input("KPI Name")
        target = st.text_input("Target Value")
        actual = st.text_input("Actual Value")
        notes = st.text_area("Notes/Actions")
        submit_kpi = st.form_submit_button("Submit KPI")

    if submit_kpi:
        # Determine Status
        try:
            actual_val = float(actual.replace('%','').replace('$',''))
            target_val = float(target.replace('%','').replace('$',''))
            if "<" in target:
                status = "Met" if actual_val < target_val else "Missed"
            elif ">" in target:
                status = "Met" if actual_val > target_val else "Missed"
            else:
                status = "Met" if actual_val == target_val else "Missed"
        except:
            status = "Check Data"

        # Save to DataFrame
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

        # Save to CSV
        kpi_data.to_csv(kpi_csv, index=False)

        st.success(f"KPI for {kpi_name} on {kpi_date} saved!")

    # Filters
    st.subheader("\U0001F5C2️ Filter KPI Records")
    filter_category = st.selectbox("Select Category", options=["All"] + list(kpi_data['Category'].unique()))
    filter_month = st.selectbox("Select Month", options=["All"] + list(kpi_data['Date'].apply(lambda x: str(x)[:7]).unique()))

    filtered_kpi_data = kpi_data.copy()
    if filter_category != "All":
        filtered_kpi_data = filtered_kpi_data[filtered_kpi_data['Category'] == filter_category]
    if filter_month != "All":
        filtered_kpi_data = filtered_kpi_data[filtered_kpi_data['Date'].apply(lambda x: str(x)[:7]) == filter_month]

    # Display the latest KPI entries with colored status and trend
    st.subheader("\U0001F4CB KPI Records:")
    def highlight_status(val):
        color = 'green' if val == 'Met' else 'red' if val == 'Missed' else 'gray'
        return f'background-color: {color}'

    if not filtered_kpi_data.empty:
        styled_kpi = filtered_kpi_data.style.applymap(highlight_status, subset=['Status'])
        st.dataframe(styled_kpi)

    # KPI Status Pie Chart
    st.subheader("\U0001F4C9 KPI Status Overview:")
    if not filtered_kpi_data.empty:
        status_counts = filtered_kpi_data['Status'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90, colors=['green', 'red', 'gray'])
        ax.axis('equal')
        st.pyplot(fig)

elif page == "Daily CTQ Tracker":
    st.title("\U0001F4C8 Daily CTQ Tracker")

    # Form for user input
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
        # Calculate Health Score
        score = 0
        score += 1 if defect_rate < 1 else 0
        score += 1 if fp_yield >= 95 else 0
        score += 1 if downtime_events == 0 else 0
        score += 1 if scrap_units <= 2 else 0
        score += 1 if calibration_misses == 0 else 0

        # Recommendation
        if score == 5:
            recommendation = "✅ Excellent - Keep it up!"
        elif 3 <= score <= 4:
            recommendation = "⚠️ Caution - Monitor closely."
        else:
            recommendation = "❌ Immediate Action Needed!"

        # Save to DataFrame
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

        # Save to CSV
        ctq_data.to_csv(ctq_csv, index=False)

        st.success(f"Entry for {entry_date} saved!")

    # Display the latest entries
    st.subheader("\U0001F4C9 Recent CTQ Records:")
    st.dataframe(ctq_data.tail(10))
