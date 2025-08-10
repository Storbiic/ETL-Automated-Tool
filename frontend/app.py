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
    display_error_message, display_success_message, fix_dataframe_types,
    create_distribution_chart, create_comparison_chart, create_processing_flow_chart,
    create_trend_analysis_chart
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
step_names = ["File Upload", "Data Preview", "Data Cleaning", "Pre-existing Items", "LOCKUP Configuration", "Results", "Master BOM Updates"]
create_progress_bar(st.session_state.current_step, len(step_names), step_names)

# Main layout
col_main, col_sidebar = st.columns([3, 1])

with col_sidebar:
    display_logs()

    st.markdown("---")

    # Clear all button
    if st.button("🗑️ Clear All Data", type="secondary"):
        with st.spinner("Clearing all data and optimizing performance..."):
            # Clear all session state
            for key in list(st.session_state.keys()):
                if key not in ['logs']:  # Keep logs for debugging
                    del st.session_state[key]
            st.session_state.current_step = 0
            st.session_state.file_id = None
            st.session_state.sheet_names = []

            # Clear all Streamlit caches for optimal performance
            st.cache_data.clear()
            st.cache_resource.clear()

            # Clear backend cache for optimal performance
            cache_result = api_client.clear_cache()
            if cache_result.get("success"):
                add_log("Backend cache cleared successfully")
            else:
                add_log("Backend cache clearing failed (server may be offline)")

            add_log("Application state and all caches cleared for optimal performance")
        st.rerun()

    # Performance optimization button
    st.markdown("---")
    st.subheader("⚡ Performance Optimization")
    if st.button("🧹 Clear Cache Only", type="secondary", help="Clear caches without losing current session data"):
        with st.spinner("Optimizing performance..."):
            # Clear Streamlit caches
            st.cache_data.clear()
            st.cache_resource.clear()

            # Clear backend cache
            cache_result = api_client.clear_cache()
            if cache_result.get("success"):
                add_log("All caches cleared for performance optimization")
                st.success("✅ Cache cleared successfully!")
            else:
                add_log("Cache clearing failed (server may be offline)")
                st.warning("⚠️ Backend cache clearing failed - server may be offline")

with col_main:
    # Step 1: File Source Selection
    st.markdown('<div class="step-header">📁 Step 1: File Source Selection</div>', unsafe_allow_html=True)

    # File source selection
    file_source = st.radio(
        "Choose file source:",
        ["📁 Local Upload", "📥 SharePoint (Manual)"],
        horizontal=True,
        help="Select whether to upload a local file or use SharePoint manual download"
    )

    if file_source == "📁 Local Upload":
        # Local file upload
        st.subheader("📁 Local File Upload")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "xls", "xlsx"],
            help="Upload your data file to begin processing"
        )
    else:  # SharePoint Manual
        # Manual SharePoint download instructions
        st.subheader("📥 SharePoint Manual Download")

        st.info("""
        **Follow these steps to use SharePoint files:**

        1. **Open SharePoint in your browser**:
           - Go to: https://uitacma.sharepoint.com/sites/YAZAKIInternship
           - Navigate to: Shared Documents folder

        2. **Download your file**:
           - Find your Excel/CSV file (e.g., MasterBOM Test.xlsx)
           - Right-click and select "Download"
           - Save it to your computer

        3. **Upload the downloaded file**:
           - Switch back to "📁 Local Upload" option above
           - Select the file you just downloaded from SharePoint
        """)

        with st.expander("🔗 Quick Links"):
            st.markdown("""
            **Direct SharePoint Links:**
            - [SharePoint Site](https://uitacma.sharepoint.com/sites/YAZAKIInternship)
            - [Shared Documents](https://uitacma.sharepoint.com/sites/YAZAKIInternship/Shared%20Documents)

            **Common Files:**
            - MasterBOM Test.xlsx
            - Target BOM files
            - Other Excel/CSV files
            """)

        st.warning("💡 **Tip**: After processing, you can manually upload the results back to SharePoint if needed.")
        uploaded_file = None  # No file upload in manual mode
    
    if uploaded_file and not st.session_state.file_id:
        with st.spinner("Uploading file..."):
            # Clear Streamlit cache before processing new file for optimal performance
            st.cache_data.clear()
            st.cache_resource.clear()
            add_log("Cache cleared for optimal performance")

            file_content = uploaded_file.read()
            result = api_client.upload_file(file_content, uploaded_file.name)

            if result.get("success"):
                st.session_state.file_id = result["file_id"]
                st.session_state.sheet_names = result["sheet_names"]
                st.session_state.current_step = 1
                add_log(f"File uploaded: {uploaded_file.name}")
                display_success_message(result["message"])

                # Clear cache again after successful upload to free memory
                st.cache_data.clear()
                add_log("Upload cache cleared for performance optimization")
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
                df = fix_dataframe_types(df)  # Fix types for Arrow compatibility
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
                df = fix_dataframe_types(df)  # Fix types for Arrow compatibility
                st.dataframe(df, use_container_width=True)

        with col2:
            st.write(f"**Target ({st.session_state.target_sheet})**")
            st.write(f"Shape: {st.session_state.clean_result['target_shape']}")
            if st.session_state.clean_result['target_preview']:
                df = pd.DataFrame(st.session_state.clean_result['target_preview'])
                df = fix_dataframe_types(df)  # Fix types for Arrow compatibility
                st.dataframe(df, use_container_width=True)

    # Column Analysis Section (after data cleaning)
    if st.session_state.current_step >= 3:
        st.markdown("---")
        st.subheader("🔍 Column Analysis for Pre-existing Items")
        st.info("Analyze status distribution for items that are in Master BOM but NOT in Target sheet")

        # Get available columns from cleaned master sheet (use actual cleaned data, not preview)
        if (st.session_state.get('clean_result') and
            st.session_state.get('file_id') and
            st.session_state.get('master_sheet')):

            try:
                # Get the actual cleaned master data from backend
                with st.spinner("Loading cleaned master data for column analysis..."):
                    # Use a simple API call to get column names from the cleaned data
                    columns_result = api_client.get_lookup_columns(
                        st.session_state.file_id,
                        st.session_state.master_sheet
                    )

                if columns_result.get("success") and columns_result.get("columns"):
                    available_columns = columns_result["columns"]
                else:
                    st.error("Failed to load columns from cleaned data")
                    available_columns = []

            except Exception as e:
                st.error(f"Error loading columns: {str(e)}")
                available_columns = []

            if available_columns:
                # Set default index if not already set
                default_index = 0
                if st.session_state.get('selected_analysis_column') in available_columns:
                    default_index = available_columns.index(st.session_state.selected_analysis_column)

                selected_analysis_column = st.selectbox(
                    "Select column for status analysis:",
                    available_columns,
                    index=default_index,
                    key="analysis_column_select",
                    help="Choose a column to analyze status distribution (X, D, 0, etc.) for items that are in Master BOM but NOT in Target sheet"
                )

                if st.button("📊 Analyze Column", type="secondary"):
                    if not selected_analysis_column:
                        st.error("Please select a valid column for analysis.")
                    elif not st.session_state.get('target_sheet'):
                        st.error("Please select a target sheet first to analyze items not in target.")
                    else:
                        with st.spinner("Analyzing column distribution for items NOT in target sheet..."):
                            # Analyze the selected column for items NOT in target sheet
                            analysis_result = api_client.analyze_column_distribution_filtered(
                                st.session_state.file_id,
                                st.session_state.master_sheet,
                                st.session_state.target_sheet,
                                selected_analysis_column
                            )

                            if analysis_result.get("success"):
                                st.session_state.column_analysis = analysis_result
                                st.session_state.selected_analysis_column = selected_analysis_column
                                add_log(f"Column analysis completed for: {selected_analysis_column}")
                                st.rerun()
                            else:
                                display_error_message("Column analysis failed", analysis_result.get("error"))
            else:
                st.warning("No columns available for analysis (only YAZAKI PN found)")
        else:
            st.info("Complete data cleaning first to enable column analysis")

        # Display column analysis results
        if st.session_state.get('column_analysis'):
            st.subheader(f"📊 Analysis Results: {st.session_state.selected_analysis_column}")
            st.info(f"📋 **Showing items in Master BOM but NOT in Target sheet** ({st.session_state.get('target_sheet', 'Unknown')})")

            analysis = st.session_state.column_analysis

            # Display filtering info
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Master Items", analysis.get("total_master_rows", 0))
            with col2:
                st.metric("Items NOT in Target", analysis.get("filtered_rows", 0))

            # Display distribution for filtered items
            st.subheader("📊 Status Distribution (Items NOT in Target Sheet)")

            # Metrics in columns
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Status 'X'", analysis["distribution"].get("X", 0),
                         help="Items with status 'X' that are not in target sheet")
            with col2:
                st.metric("Status 'D'", analysis["distribution"].get("D", 0),
                         help="Items with status 'D' that are not in target sheet")
            with col3:
                st.metric("Status '0'", analysis["distribution"].get("0", 0),
                         help="Items with status '0' that are not in target sheet")
            with col4:
                st.metric("Other/Empty", analysis["distribution"].get("OTHER", 0),
                         help="Items with other/empty status that are not in target sheet")

            # Visual chart
            chart = create_distribution_chart(
                analysis["distribution"],
                f"Status Distribution - Items NOT in Target ({analysis.get('filtered_rows', 0)} items)"
            )
            if chart:
                st.plotly_chart(chart, use_container_width=True)

            # Show detailed breakdown
            if analysis.get("detailed_breakdown"):
                with st.expander("📋 Detailed Breakdown"):
                    breakdown_df = pd.DataFrame(analysis["detailed_breakdown"])
                    breakdown_df = fix_dataframe_types(breakdown_df)
                    st.dataframe(breakdown_df, use_container_width=True)

    # Step 3.5: Process Pre-existing Items
    if st.session_state.current_step >= 3 and st.session_state.get('selected_analysis_column'):
        st.markdown('<div class="step-header">🔄 Step 3.5: Process Pre-existing Items</div>', unsafe_allow_html=True)

        st.info(f"""
        **Process Logic**: Update items in Master BOM that are:
        - **Not present** in the Target sheet ({st.session_state.get('target_sheet', 'Unknown')})
        - **Currently have status 'X'** in column '{st.session_state.selected_analysis_column}'
        - **Will be updated to status 'D'** (discontinued)

        Based on your analysis: **{st.session_state.get('column_analysis', {}).get('distribution', {}).get('X', 0)} items**
        with status 'X' are not in the target sheet and will be updated.
        """)

        # Show current analysis
        if st.session_state.get('column_analysis'):
            analysis = st.session_state.column_analysis

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current 'X' Status", analysis["distribution"].get("X", 0))
            with col2:
                st.metric("Current 'D' Status", analysis["distribution"].get("D", 0))
            with col3:
                st.metric("Target Sheet", st.session_state.get('target_sheet', 'Not selected'))

        # Process pre-existing items
        if st.button("🔄 Process Pre-existing Items", type="primary"):
            if not st.session_state.get('target_sheet'):
                st.error("Please select a target sheet first in Step 2")
            else:
                with st.spinner("Processing pre-existing items..."):
                    process_result = api_client.process_preexisting_items(
                        st.session_state.file_id,
                        st.session_state.master_sheet,
                        st.session_state.target_sheet,
                        st.session_state.selected_analysis_column
                    )

                    if process_result.get("success"):
                        st.session_state.preexisting_result = process_result
                        st.session_state.current_step = 3.5
                        add_log(f"Pre-existing items processed: {process_result['updated_count']} items updated")
                        display_success_message(process_result["message"])
                        st.rerun()
                    else:
                        display_error_message("Pre-existing processing failed", process_result.get("error"))

        # Show processing results
        if st.session_state.get('preexisting_result'):
            result = st.session_state.preexisting_result

            st.subheader("📊 Processing Results")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Items Updated", result["updated_count"])
            with col2:
                st.metric("X → D Changes", result["updated_count"])
            with col3:
                st.metric("Items Checked", result["total_checked"])
            with col4:
                st.metric("Not in Target", result["not_in_target_count"])

            # Show updated analysis with comparison and visuals
            if result.get("new_distribution") and result.get("original_distribution"):
                st.subheader("📈 Distribution Comparison with Visual Analytics")

                # Create comparison chart
                comparison_chart = create_comparison_chart(
                    result["original_distribution"],
                    result["new_distribution"]
                )
                if comparison_chart:
                    st.plotly_chart(comparison_chart, use_container_width=True)

                # Processing flow chart
                processing_flow = create_processing_flow_chart(result)
                if processing_flow:
                    st.plotly_chart(processing_flow, use_container_width=True)

                # Detailed metrics in columns
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**📊 Before Processing (Entire Master BOM)**")
                    orig = result["original_distribution"]
                    st.metric("Original 'X' Count", orig.get("X", 0))
                    st.metric("Original 'D' Count", orig.get("D", 0))
                    st.metric("Status '0'", orig.get("0", 0))
                    st.metric("Other/Empty", orig.get("OTHER", 0))

                    # Before processing pie chart
                    before_chart = create_distribution_chart(
                        orig, "Before Processing Distribution"
                    )
                    if before_chart:
                        st.plotly_chart(before_chart, use_container_width=True)

                with col2:
                    st.write("**📊 After Processing (Entire Master BOM)**")
                    new = result["new_distribution"]

                    # Calculate deltas
                    x_delta = new.get("X", 0) - orig.get("X", 0)
                    d_delta = new.get("D", 0) - orig.get("D", 0)

                    st.metric("New 'X' Count", new.get("X", 0), delta=x_delta)
                    st.metric("New 'D' Count", new.get("D", 0), delta=d_delta)
                    st.metric("Status '0'", new.get("0", 0))
                    st.metric("Other/Empty", new.get("OTHER", 0))

                    # After processing pie chart
                    after_chart = create_distribution_chart(
                        new, "After Processing Distribution"
                    )
                    if after_chart:
                        st.plotly_chart(after_chart, use_container_width=True)



            elif result.get("new_distribution"):
                # Fallback to simple display if original distribution not available
                st.subheader("📈 Updated Distribution")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("New 'X' Count", result["new_distribution"].get("X", 0))
                with col2:
                    st.metric("New 'D' Count", result["new_distribution"].get("D", 0))
                with col3:
                    st.metric("Status '0'", result["new_distribution"].get("0", 0))
                with col4:
                    st.metric("Other/Empty", result["new_distribution"].get("OTHER", 0))

            # Show preview of updated items
            if result.get("updated_items_preview"):
                with st.expander(f"📋 Preview of Updated Items ({len(result['updated_items_preview'])} shown)"):
                    preview_df = pd.DataFrame(result["updated_items_preview"])
                    preview_df = fix_dataframe_types(preview_df)
                    st.dataframe(preview_df, use_container_width=True)

            # Rollback and Continue options
            col1, col2 = st.columns(2)

            with col1:
                # Check rollback availability
                rollback_status = api_client.get_rollback_status(st.session_state.file_id)
                if rollback_status.get("rollback_available", False):
                    if st.button("🔄 Rollback Changes", type="secondary", help="Restore Master BOM to state before processing"):
                        with st.spinner("Rolling back changes..."):
                            rollback_result = api_client.rollback_preexisting_changes(
                                st.session_state.file_id,
                                st.session_state.master_sheet
                            )

                            if rollback_result.get("success"):
                                # Clear the processing result to hide the section
                                if 'preexisting_result' in st.session_state:
                                    del st.session_state['preexisting_result']

                                add_log(f"Rollback completed: {rollback_result['message']}")
                                display_success_message("Rollback completed successfully")
                                st.info(f"📅 Restored to backup from: {rollback_result.get('backup_timestamp', 'Unknown')}")
                                st.rerun()
                            else:
                                display_error_message("Rollback failed", rollback_result.get("error"))
                else:
                    st.info("No rollback available")

            with col2:
                # Continue to LOCKUP
                if st.button("➡️ Continue to LOCKUP Configuration", type="primary"):
                    st.session_state.current_step = 4
                    add_log("Proceeding to LOCKUP configuration")
                    st.rerun()

    # Step 4: LOCKUP Configuration
    if st.session_state.current_step >= 4:
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
                        st.session_state.key_column = "YAZAKI PN"  # Standard key column for YAZAKI
                        st.session_state.current_step = 5
                        add_log(f"LOCKUP completed using column: {lookup_column}")
                        display_success_message(lookup_result["message"])
                        st.rerun()
                    else:
                        display_error_message("LOCKUP failed", lookup_result.get("error"))

    # Step 5: Results
    if st.session_state.get('lookup_result') and st.session_state.current_step >= 5:
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
    if st.session_state.get('lookup_result') and st.session_state.current_step >= 5:
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
