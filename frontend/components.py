"""
Reusable UI components for the Streamlit frontend
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import datetime


def add_log(message: str):
    """Add a timestamped log entry"""
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")


def display_logs():
    """Display activity logs in sidebar"""
    with st.sidebar:
        st.subheader("📋 Activity Logs")
        
        if st.session_state.get('logs', []):
            # Show last 15 logs in reverse order (newest first)
            for log in reversed(st.session_state.logs[-15:]):
                st.text(log)
        else:
            st.text("No activity yet...")
        
        if st.button("Clear Logs", key="clear_logs"):
            st.session_state.logs = []
            st.rerun()


def display_kpi_metrics(kpi_counts: Dict[str, int], total_records: int):
    """Display KPI metrics in columns"""
    st.subheader("📊 Activation Status KPIs")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Records", total_records)
    with col2:
        st.metric("Status '0'", kpi_counts.get('0', 0))
    with col3:
        st.metric("Status 'D'", kpi_counts.get('D', 0))
    with col4:
        st.metric("Status 'X'", kpi_counts.get('X', 0))
    with col5:
        st.metric("Not Found", kpi_counts.get('NOT_FOUND', 0))


def create_status_chart(kpi_counts: Dict[str, int]):
    """Create a bar chart for activation status distribution"""
    if not kpi_counts:
        return None

    # Prepare data for chart
    labels = list(kpi_counts.keys())
    values = list(kpi_counts.values())

    # Create bar chart
    fig = px.bar(
        x=labels,
        y=values,
        title="Activation Status Distribution",
        color=labels,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_layout(
        showlegend=False,
        height=400,
        font=dict(size=12),
        xaxis_title="Activation Status",
        yaxis_title="Count"
    )

    # Add value labels on bars
    fig.update_traces(texttemplate='%{y}', textposition='outside')

    return fig


def display_dataframe_with_search(df: pd.DataFrame, key: str):
    """Display dataframe with search functionality"""
    if df.empty:
        st.warning("No data to display")
        return

    # Search functionality
    search_term = st.text_input(
        "🔍 Search in data:",
        key=f"search_{key}",
        help="Search across all columns"
    )

    # Filter dataframe based on search
    if search_term:
        # Create a mask for rows containing the search term in any column
        mask = df.astype(str).apply(
            lambda x: x.str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        filtered_df = df[mask]

        if filtered_df.empty:
            st.warning(f"No results found for '{search_term}'")
            return
        else:
            st.info(f"Found {len(filtered_df)} results for '{search_term}'")
    else:
        filtered_df = df

    # Display total count
    st.write(f"**Total records:** {len(filtered_df)}")

    # Display the dataframe
    st.dataframe(filtered_df, use_container_width=True, height=400)


def create_progress_bar(current_step: int, total_steps: int, step_names: List[str]):
    """Create a progress bar showing current step"""
    progress = current_step / total_steps
    
    st.progress(progress)
    
    # Show step indicators
    cols = st.columns(total_steps)
    for i, (col, step_name) in enumerate(zip(cols, step_names)):
        with col:
            if i < current_step:
                st.success(f"✅ {step_name}")
            elif i == current_step:
                st.info(f"🔄 {step_name}")
            else:
                st.write(f"⏳ {step_name}")


def display_file_info(filename: str, sheet_names: List[str]):
    """Display file information in an info box"""
    st.info(f"""
    **File:** {filename}  
    **Sheets:** {len(sheet_names)}  
    **Sheet Names:** {', '.join(sheet_names)}
    """)


def create_download_section(download_url: str, filename: str, data_preview: List[Dict]):
    """Create download section with preview"""
    st.subheader("📥 Download Results")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**File:** {filename}")
        st.write(f"**Records:** {len(data_preview)}")
    
    with col2:
        st.download_button(
            label="📥 Download CSV",
            data="",  # This would be populated with actual data
            file_name=filename,
            mime="text/csv",
            help="Download the complete processed dataset"
        )


def display_error_message(error: str, details: str = None):
    """Display error message with optional details"""
    st.error(f"❌ {error}")
    if details:
        with st.expander("Error Details"):
            st.code(details)


def display_success_message(message: str):
    """Display success message"""
    st.success(f"✅ {message}")


def create_sidebar_navigation():
    """Create sidebar navigation menu"""
    with st.sidebar:
        st.title("🔧 ETL Automation Tool")
        
        # Navigation menu
        selected = st.selectbox(
            "Navigation",
            ["📁 File Upload", "🧹 Data Cleaning", "🔍 Data Lookup", "📊 Results"],
            key="navigation"
        )
        
        return selected.split(" ", 1)[1]  # Return just the text part
