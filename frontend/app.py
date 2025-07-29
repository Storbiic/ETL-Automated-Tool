"""
Enhanced Streamlit frontend for ETL Automation Tool
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Any
import time

from api_client import api_client
from components import (
    add_log, display_logs, display_kpi_metrics, create_status_chart,
    display_dataframe_with_search, create_progress_bar, display_file_info,
    display_error_message, display_success_message
)

# Page configuration
st.set_page_config(
    page_title="ETL Automation Tool v2.0",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        color: #2e8b57;
        border-bottom: 2px solid #2e8b57;
        padding-bottom: 0.5rem;
        margin: 1rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'file_id' not in st.session_state:
    st.session_state.file_id = None
if 'sheet_names' not in st.session_state:
    st.session_state.sheet_names = []

# Main header
st.markdown('<h1 class="main-header">🔧 ETL Automation Tool v2.0</h1>', unsafe_allow_html=True)

# Check API connection
if not api_client.health_check():
    st.error("❌ Cannot connect to backend API. Please ensure the FastAPI server is running on http://localhost:8000")
    st.stop()

# Progress tracking
step_names = ["File Upload", "Data Preview", "Data Cleaning", "LOCKUP Configuration", "Results", "Master BOM Updates"]
create_progress_bar(st.session_state.current_step, len(step_names), step_names)

# Main layout
col_main, col_sidebar = st.columns([3, 1])

with col_sidebar:
    display_logs()
    
    # Clear all button
    if st.button("🗑️ Clear All", type="secondary"):
        for key in list(st.session_state.keys()):
            if key not in ['logs']:  # Keep logs for debugging
                del st.session_state[key]
        st.session_state.current_step = 0
        st.session_state.file_id = None
        st.session_state.sheet_names = []
        add_log("Application state cleared")
        st.rerun()

with col_main:
    # Step 1: File Upload
    st.markdown('<div class="step-header">📁 Step 1: File Upload</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xls", "xlsx"],
        help="Upload your data file to begin processing"
    )
    
    if uploaded_file and not st.session_state.file_id:
        with st.spinner("Uploading file..."):
            file_content = uploaded_file.read()
            result = api_client.upload_file(file_content, uploaded_file.name)
            
            if result.get("success"):
                st.session_state.file_id = result["file_id"]
                st.session_state.sheet_names = result["sheet_names"]
                st.session_state.current_step = 1
                add_log(f"File uploaded: {uploaded_file.name}")
                display_success_message(result["message"])
                st.rerun()
            else:
                display_error_message("File upload failed", result.get("error"))
    
    # Step 2: Data Preview and Sheet Selection
    if st.session_state.file_id and st.session_state.current_step >= 1:
        st.markdown('<div class="step-header">👀 Step 2: Data Preview & Sheet Selection</div>', unsafe_allow_html=True)
        
        display_file_info(uploaded_file.name if uploaded_file else "Unknown", st.session_state.sheet_names)
        
        # Sheet selection
        col1, col2 = st.columns(2)
        
        with col1:
            master_sheet = st.selectbox(
                "Select Master BOM Sheet",
                st.session_state.sheet_names,
                key="master_sheet_select"
            )
        
        with col2:
            target_options = [s for s in st.session_state.sheet_names if s != master_sheet]
            target_sheet = st.selectbox(
                "Select Target Sheet",
                target_options,
                key="target_sheet_select"
            )
        
        # Preview button
        if st.button("👀 Preview Selected Sheets", type="primary"):
            with st.spinner("Loading preview..."):
                preview_result = api_client.preview_sheets(
                    st.session_state.file_id, 
                    [master_sheet, target_sheet]
                )
                
                if preview_result.get("success"):
                    st.session_state.preview_data = preview_result["previews"]
                    st.session_state.master_sheet = master_sheet
                    st.session_state.target_sheet = target_sheet
                    st.session_state.current_step = 2
                    add_log(f"Previewed sheets: {master_sheet}, {target_sheet}")
                    st.rerun()
                else:
                    display_error_message("Preview failed", preview_result.get("error"))
    
    # Display preview data
    if st.session_state.get('preview_data') and st.session_state.current_step >= 2:
        st.subheader("📋 Sheet Previews")
        
        for sheet_name, data in st.session_state.preview_data.items():
            st.write(f"**{sheet_name}**")
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning(f"No data in {sheet_name}")
    
    # Step 3: Data Cleaning
    if st.session_state.current_step >= 2:
        st.markdown('<div class="step-header">🧹 Step 3: Data Cleaning</div>', unsafe_allow_html=True)
        
        if st.button("🧹 Clean Data", type="primary"):
            with st.spinner("Cleaning data..."):
                clean_result = api_client.clean_data(
                    st.session_state.file_id,
                    st.session_state.master_sheet,
                    st.session_state.target_sheet
                )
                
                if clean_result.get("success"):
                    st.session_state.clean_result = clean_result
                    st.session_state.current_step = 3
                    add_log("Data cleaning completed")
                    display_success_message(clean_result["message"])
                    st.rerun()
                else:
                    display_error_message("Cleaning failed", clean_result.get("error"))

    # Display cleaning results
    if st.session_state.get('clean_result') and st.session_state.current_step >= 3:
        st.subheader("🧹 Cleaning Results")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Master ({st.session_state.master_sheet}) - YAZAKI PN only**")
            st.write(f"Shape: {st.session_state.clean_result['master_shape']}")
            if st.session_state.clean_result['master_preview']:
                df = pd.DataFrame(st.session_state.clean_result['master_preview'])
                st.dataframe(df, use_container_width=True)

        with col2:
            st.write(f"**Target ({st.session_state.target_sheet})**")
            st.write(f"Shape: {st.session_state.clean_result['target_shape']}")
            if st.session_state.clean_result['target_preview']:
                df = pd.DataFrame(st.session_state.clean_result['target_preview'])
                st.dataframe(df, use_container_width=True)

    # Step 4: LOCKUP Configuration
    if st.session_state.current_step >= 3:
        st.markdown('<div class="step-header">🔍 Step 4: LOCKUP Configuration</div>', unsafe_allow_html=True)

        # Get available columns automatically
        if not st.session_state.get('available_columns'):
            with st.spinner("Loading available columns..."):
                columns_result = api_client.get_lookup_columns(
                    st.session_state.file_id,
                    st.session_state.master_sheet
                )

                if columns_result.get("success"):
                    st.session_state.available_columns = columns_result["columns"]
                    add_log("Loaded available columns for LOCKUP")
                else:
                    display_error_message("Failed to load columns", columns_result.get("error"))

        # Column selection only
        if st.session_state.get('available_columns'):
            lookup_column = st.selectbox(
                "Select LOCKUP column:",
                st.session_state.available_columns,
                key="lookup_column_select",
                help="Choose the column from Master BOM to lookup values"
            )

            # Perform LOCKUP
            if st.button("🚀 Perform LOCKUP", type="primary"):
                with st.spinner("Performing LOCKUP..."):
                    lookup_result = api_client.perform_lookup(
                        st.session_state.file_id,
                        st.session_state.master_sheet,
                        st.session_state.target_sheet,
                        lookup_column
                    )

                    if lookup_result.get("success"):
                        st.session_state.lookup_result = lookup_result
                        st.session_state.lookup_column = lookup_column
                        st.session_state.current_step = 4
                        add_log(f"LOCKUP completed using column: {lookup_column}")
                        display_success_message(lookup_result["message"])
                        st.rerun()
                    else:
                        display_error_message("LOCKUP failed", lookup_result.get("error"))

    # Step 5: Results
    if st.session_state.get('lookup_result') and st.session_state.current_step >= 4:
        st.markdown('<div class="step-header">📊 Step 5: Results</div>', unsafe_allow_html=True)

        result = st.session_state.lookup_result

        # Display KPIs
        display_kpi_metrics(result["kpi_counts"], result["total_records"])

        # Display chart
        chart = create_status_chart(result["kpi_counts"])
        if chart:
            st.plotly_chart(chart, use_container_width=True)

        # Display results table with search
        st.subheader("📋 Processed Data")
        if result["result_preview"]:
            df = pd.DataFrame(result["result_preview"])
            display_dataframe_with_search(df, "results")

        # Download section
        st.subheader("📥 Download Results")
        download_filename = f"processed_{st.session_state.target_sheet}.csv"

        if st.button("📥 Download Complete Dataset", type="primary"):
            with st.spinner("Preparing download..."):
                download_data = api_client.download_data(
                    st.session_state.file_id,
                    st.session_state.target_sheet
                )

                if download_data:
                    st.download_button(
                        label="📥 Download CSV File",
                        data=download_data,
                        file_name=download_filename,
                        mime="text/csv",
                        help="Download the complete processed dataset"
                    )
                    add_log(f"Dataset ready for download: {download_filename}")
                else:
                    st.error("Failed to prepare download")

    # Step 6: Master BOM Updates
    if st.session_state.get('lookup_result') and st.session_state.current_step >= 4:
        st.markdown('<div class="step-header">🔄 Step 6: Master BOM Updates</div>', unsafe_allow_html=True)

        result = st.session_state.lookup_result

        # Show status breakdown for updates
        st.subheader("📊 Update Operations Summary")

        status_counts = result["kpi_counts"]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Status 'X' (No Update)", status_counts.get('X', 0), help="Records that will not be updated")
        with col2:
            st.metric("Status 'D' (Update)", status_counts.get('D', 0), help="Records that will update existing entries")
        with col3:
            st.metric("Status '0' (Check/Insert)", status_counts.get('0', 0), help="Records to check for duplicates or insert")
        with col4:
            st.metric("Not Found (Insert)", status_counts.get('NOT_FOUND', 0), help="Records to insert as new entries")

        # Process updates button
        if st.button("🔄 Process Master BOM Updates", type="primary"):
            with st.spinner("Processing Master BOM updates..."):
                update_result = api_client.process_master_updates(
                    st.session_state.file_id,
                    st.session_state.master_sheet,
                    st.session_state.target_sheet,
                    st.session_state.lookup_column
                )

                if update_result.get("success"):
                    st.session_state.update_result = update_result
                    st.session_state.current_step = 5
                    add_log("Master BOM updates completed")
                    display_success_message(update_result["message"])
                    st.rerun()
                else:
                    display_error_message("Master BOM update failed", update_result.get("error"))

    # Display update results
    if st.session_state.get('update_result') and st.session_state.current_step >= 5:
        st.subheader("✅ Update Results")

        update_result = st.session_state.update_result

        # Show update statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Records Updated", update_result.get("updated_count", 0))
        with col2:
            st.metric("Records Inserted", update_result.get("inserted_count", 0))
        with col3:
            st.metric("Duplicates Found", update_result.get("duplicates_count", 0))
        with col4:
            st.metric("Skipped (X status)", update_result.get("skipped_count", 0))

        # Show duplicates if any
        if update_result.get("duplicates") and len(update_result["duplicates"]) > 0:
            st.subheader("⚠️ Duplicate Records Found")
            st.warning("The following records were found to be duplicates and require review:")

            duplicates_df = pd.DataFrame(update_result["duplicates"])
            display_dataframe_with_search(duplicates_df, "duplicates")

        # Download updated Master BOM
        st.subheader("📥 Download Updated Master BOM")
        if st.button("📥 Download Updated Master BOM", type="primary"):
            with st.spinner("Preparing updated Master BOM..."):
                download_data = api_client.download_data(
                    st.session_state.file_id,
                    st.session_state.master_sheet
                )

                if download_data:
                    st.download_button(
                        label="📥 Download Updated Master BOM",
                        data=download_data,
                        file_name=f"updated_{st.session_state.master_sheet}.csv",
                        mime="text/csv",
                        help="Download the updated Master BOM with all changes applied"
                    )
                    add_log(f"Updated Master BOM ready for download")
                else:
                    st.error("Failed to prepare Master BOM download")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.8rem;">'
    'ETL Automation Tool v2.0 | Powered by FastAPI & Streamlit'
    '</div>',
    unsafe_allow_html=True
)
