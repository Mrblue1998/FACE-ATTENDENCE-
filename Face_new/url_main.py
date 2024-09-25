import json
import streamlit as st
import datetime
import pandas as pd
from processor.__DatabaseLayer__ import DataAccess
import time

# Streamlit App
st.title("Face Attendance")

# Placeholder for the table
table_placeholder = st.empty()

# Initial data structure
data = {'Name': [], 'In_time': [], 'Out_time': []}

# User input for the video source
video_source = st.text_input(
    "Enter Video Source (0 for webcam, RTSP URL, or file path)", value="0"
)

DataAccess.db_details()
# Fetch attendance data based on the current date
def fetch_attendance_data():
    cur_date = datetime.datetime.now()
    attendance_db_data = DataAccess.get_attendance_data_by_date(cur_date)
    if attendance_db_data:
        attendance_blob = attendance_db_data["person_details"]
        time_data = json.loads(attendance_blob)

        # Clear old data
        data['Name'].clear()
        data['In_time'].clear()
        data['Out_time'].clear()

        # Populate the table with updated data
        for name, time_person in time_data.items():
            data['Name'].append(name)
            data['In_time'].append(time_person[0][0])
            data['Out_time'].append(time_person[-1][0])

        # Convert data to a DataFrame
        df = pd.DataFrame(data)
        return df
    else:
        return pd.DataFrame(data)


# Initial call to display the table
df = fetch_attendance_data()
table_placeholder.dataframe(df)

# Submit button
if st.button("Start Video Feed"):
    # Pass the video source as a URL parameter to the Flask app
    video_url = f"http://127.0.0.1:5000/video_feed?source={video_source}"

    # Display the video feed using an HTML <img> tag
    st.markdown(f"""
        <div style="text-align:center">
            <img src="{video_url}" width="700">
        </div>
        """, unsafe_allow_html=True)

# Periodically refresh the table to check for updated "Out_time"
REFRESH_INTERVAL = 5  # Refresh every 5 seconds

while True:
    # Re-fetch data and update the table
    df = fetch_attendance_data()
    table_placeholder.dataframe(df)

    # Sleep for the refresh interval
    time.sleep(REFRESH_INTERVAL)
