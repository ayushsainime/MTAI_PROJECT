import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set page configuration for a wider layout
st.set_page_config(layout="wide")

# --- Title and Subheading ---
st.title("Workshop Tool Usage Analysis Dashboard")
st.subheader("an interactive tool to view tool usage and analysis  ")
st.subheader("----------------------------------------------- ")

st.subheader("MTAI PROJECT GROUP 2 ")

st.markdown("""
**1. Single Point Cutting Tool (Turning)**
- **Tool Material:** Coated Carbide (P-grade TiN/TiAlN)
- **Cutting Speed (V):** 150 m/min
- **Feed (f):** 0.25 mm/rev
- **Depth of Cut (ap):** 2 mm
- **Tool Life:** ≈ 60 minutes
- **Work Material:** Mild Steel (AISI 1045)

**2. Milling Cutter (End Milling)**
- **Tool Material:** Solid Carbide (TiAlN coated)
- **Cutting Speed (V):** 180 m/min
- **Feed per Tooth (fₙ):** 0.06 mm/tooth
- **Axial Depth (ap):** 3 mm
- **Radial Depth (ae):** 2 mm
- **Tool Life:** ≈ 90 minutes
- **Work Material:** Mild Steel (AISI 1045)

**3. Drilling Bit (Twist Drill)**
- **Tool Material:** Cobalt HSS (M35)
- **Cutting Speed (V):** 25 m/min
- **Feed (f):** 0.20 mm/rev
- **Tool Life:** ≈ 25 minutes
- **Work Material:** Mild Steel (AISI 1045)
""")

# --- Data Loading and Caching ---
@st.cache_data
def load_initial_data(file_path):
    """Loads the initial data from the Excel file."""
    return pd.read_excel(file_path)

@st.cache_data
def perform_feature_engineering(df_initial):
    """Performs all the feature engineering steps from the notebook."""
    df = df_initial.copy()
    # Ensure Input/Output times are datetime
    df["Input Time"] = pd.to_datetime(df["Input Time"])
    df["Output Time"] = pd.to_datetime(df["Output Time"])

    # Feature 1: Usage Duration (minutes)
    df["Usage Duration (min)"] = (df["Output Time"] - df["Input Time"]).dt.total_seconds() / 60

    # Feature 2: Idle Time (minutes)
    df = df.sort_values(by=["Tool Type", "Location", "Input Time"])
    df["Prev Output Time"] = df.groupby(["Tool Type", "Location"])["Output Time"].shift(1)
    df["Idle Time (min)"] = (df["Input Time"] - df["Prev Output Time"]).dt.total_seconds() / 60
    df["Idle Time (min)"] = df["Idle Time (min)"].clip(lower=0)
    df.drop(columns=["Prev Output Time"], inplace=True)
    df.fillna(0, inplace=True)

    # Feature 3: Daily Usage Frequency
    df["Date"] = pd.to_datetime(df["Input Time"].dt.date)
    daily_usage = df.groupby(["Tool Type", "Location", "Date"]).size().reset_index(name="Daily Usage Frequency")
    df = df.merge(daily_usage, on=["Tool Type", "Location", "Date"], how="left")

    # Feature 4: Cumulative Usage per Tool (minutes)
    df["Cumulative Usage (min)"] = df.groupby(["Tool Type", "Location"])["Usage Duration (min)"].cumsum()

    # Feature 5: Daily total usage time (minutes)
    daily_usage_time = df.groupby(["Tool Type", "Location", "Date"])["Usage Duration (min)"].sum().reset_index(name="Daily Usage (min)")
    df = df.merge(daily_usage_time, on=["Tool Type", "Location", "Date"], how="left")

    # Feature 6: Tool Life
    df["Tool Type"] = df["Tool Type"].str.strip().str.lower()
    tool_life = {
        "single point cutting tool": 120,
        "drilling bit": 60,
        "milling cutter": 180
    }
    df["Tool Life (min)"] = df["Tool Type"].map(tool_life)

    # Rearrange columns for readability
    cols = [
        "Input Time", "Output Time", "Date", "Location", "Tool Type",
        "Usage Duration (min)", "Idle Time (min)", "Daily Usage Frequency",
        "Cumulative Usage (min)", "Daily Usage (min)", "Tool Life (min)"
    ]
    final_df = df[cols].copy()
    return final_df

# Load the data
try:
    initial_df = load_initial_data("tool_usage_data.xlsx")
    final_df = perform_feature_engineering(initial_df)

    # --- Display DataFrames ---
    with st.expander("Show Initial Data (df)"):
        st.dataframe(initial_df)

    with st.expander("Show Final Data after Feature Engineering (final_df)"):
        st.dataframe(final_df)

    # --- Plotting Section ---
    st.header("Visual Analysis")

    # Layout for the first row of charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Daily Usage Trends")
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=final_df, x='Date', y='Daily Usage (min)', hue='Tool Type', ax=ax1)
        ax1.tick_params(axis='x', rotation=45)
        st.pyplot(fig1)

    with col2:
        st.subheader("Tool Efficiency (Active vs. Idle Time)")
        df_melt = final_df.melt(id_vars=['Tool Type'],
                                value_vars=['Usage Duration (min)', 'Idle Time (min)'],
                                var_name='Type', value_name='Time (min)')
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.barplot(data=df_melt, x='Tool Type', y='Time (min)', hue='Type', ax=ax2)
        st.pyplot(fig2)


    # Layout for the second row of charts
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Usage Distribution per Tool and Workshop")
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=final_df, x='Tool Type', y='Daily Usage (min)', hue='Location', ax=ax3)
        st.pyplot(fig3)

    with col4:
        st.subheader("Daily Usage Frequency Pattern")
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        sns.barplot(data=final_df, x='Tool Type', y='Daily Usage Frequency', hue='Location', ax=ax4)
        st.pyplot(fig4)

    # Heatmap and Pairplot (Wider components)
    st.subheader("Heatmap: Tool Usage Over Time")
    usage_pivot = final_df.pivot_table(values='Daily Usage (min)', index='Tool Type', columns='Date')
    fig5, ax5 = plt.subplots(figsize=(12, 6))
    sns.heatmap(usage_pivot, cmap='YlGnBu', ax=ax5)
    st.pyplot(fig5)

    st.subheader("Pairplot for Quick Relationship Overview")
    pairplot_vars = [
        'Usage Duration (min)', 'Idle Time (min)',
        'Daily Usage (min)', 'Cumulative Usage (min)', 'Tool Life (min)'
    ]
    # Using st.spinner for potentially long-running plots
    with st.spinner('Generating Pairplot...'):
        fig6 = sns.pairplot(final_df, hue='Tool Type', vars=pairplot_vars, height=2)
        st.pyplot(fig6)

except FileNotFoundError:
    st.error("The data file 'tool_usage_data.xlsx' was not found. Please make sure it's in the same directory as the app.")
except Exception as e:
    st.error(f"An error occurred: {e}")


