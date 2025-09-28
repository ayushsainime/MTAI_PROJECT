## 🛠️ RFID-Based Tool Tracking System GROUP -2 
# Project Overview

This project is an IoT-based tool monitoring system designed for shop floors and manufacturing environments.
It records the check-in and check-out times of tools using RFID technology and stores the data in the cloud.
A Streamlit dashboard is then used to visualize the logs, tool availability, and usage statistics in real time.

# Features

 RFID-based tracking – Each tool is tagged with an RFID card/keyfob.

 Automatic check-in & check-out – Logs timestamps when tools are borrowed or returned.

 Cloud storage – Data stored in Google Sheets / Firebase for easy access.

 Streamlit dashboard – Displays live tool status, usage history, and total duration.

 Low-cost implementation – Total hardware cost under ₹2000.

# System Architecture

ESP32 + RFID Reader (MFRC522) scans tool tags.

ESP32 firmware (via Arduino IDE) sends log data (Tool ID, In/Out event, Timestamp) to the cloud.

Google Sheets / Firebase stores the events in real time.

Streamlit dashboard fetches data and visualizes:

Tool currently in use / available

Total usage time per tool


# ⚙️ Technologies Used

Arduino IDE – For programming the ESP32 firmware.

Google Sheets / Firebase – For storing check-in/out logs.

Python – For backend processing of usage data.

Streamlit – For building the interactive dashboard.

VS Code – For managing Python and ESP32 code.

GitHub – For version control and project collaboration.

Python Libraries – pandas, matplotlib, gspread, streamlit

Historical log of check-in/check-out

