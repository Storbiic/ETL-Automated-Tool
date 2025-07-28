import streamlit as st
import requests
import pandas as pd
import json
from typing import Dict, Any, List
import io
import time
import plotly.express as px
import plotly.graph_objects as go

# Configure Streamlit page
st.set_page_config(
    page_title="ETL Data Processing Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #ffeaa7;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def check_api_connection():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_file_to_api(uploaded_file):
    """Upload file to FastAPI backend"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error uploading file: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None
def sanitize_dataframe_for_plot(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]):
            df[col] = df[col].astype(str)
    return df


def get_data_from_api(file_id: str, sheet_name: str, limit: int = 100):
    """Get data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/data/{file_id}/{sheet_name}?limit={limit}", timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error getting data: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def apply_filters_api(file_id: str, sheet_name: str, filters: Dict):
    """Apply filters via API"""
    try:
        payload = {
            "file_id": file_id,
            "sheet_name": sheet_name,
            "filters": filters
        }
        response = requests.post(f"{API_BASE_URL}/filter", json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error applying filters: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def join_sheets_api(file_id: str, left_sheet: str, right_sheet: str, left_key: str, right_key: str, join_type: str):
    """Join sheets via API"""
    try:
        payload = {
            "file_id": file_id,
            "left_sheet": left_sheet,
            "right_sheet": right_sheet,
            "left_key": left_key,
            "right_key": right_key,
            "join_type": join_type
        }
        response = requests.post(f"{API_BASE_URL}/join", json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error joining sheets: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def download_data_from_api(file_id: str, sheet_name: str):
    """Download data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/download/{file_id}/{sheet_name}", timeout=30)
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Error downloading data: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def render_data_overview(df_data: Dict, sheet_name: str):
    """Render data overview with charts"""
    df = pd.DataFrame(df_data['data'])
    
    if df.empty:
        st.warning("No data to display")
        return
    
    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", df_data['total_rows'])
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Numeric Columns", len([col for col in df.columns if df[col].dtype in ['int64', 'float64']]))
    with col4:
        st.metric("Text Columns", len([col for col in df.columns if df[col].dtype == 'object']))
    
    # Data preview
    st.subheader("Data Preview")
    st.dataframe(df, use_container_width=True, height=400)
    
    # Quick visualizations for numeric columns
    numeric_cols = [col for col in df.columns if df[col].dtype in ['int64', 'float64']]
    if numeric_cols:
        st.subheader("Quick Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if len(numeric_cols) >= 1:
                # Distribution plot for first numeric column
                fig = px.histogram(df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if len(numeric_cols) >= 2:
                # Scatter plot for first two numeric columns
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], 
                               title=f"{numeric_cols[0]} vs {numeric_cols[1]}")
                st.plotly_chart(fig, use_container_width=True)
            elif len(numeric_cols) == 1:
                # Box plot for single numeric column
                fig = px.box(df, y=numeric_cols[0], title=f"Box Plot of {numeric_cols[0]}")
                st.plotly_chart(fig, use_container_width=True)

def render_filters_sidebar(sheet_metadata: Dict, key_prefix: str) -> Dict:
    """Render filter controls in sidebar"""
    st.sidebar.subheader("🔍 Apply Filters")
    
    filters = {}
    filter_metadata = sheet_metadata.get('filters', {})
    
    for col_name, filter_config in filter_metadata.items():
        filter_type = filter_config.get('type', 'categorical')
        
        st.sidebar.write(f"**{col_name}**")
        
        if filter_type == 'categorical':
            options = filter_config.get('options', [])
            if options:
                selected = st.sidebar.multiselect(
                    f"Select values:",
                    options=options,
                    key=f"{key_prefix}_{col_name}_categorical",
                    help=f"Filter {col_name} by selecting specific values"
                )
                if selected:
                    filters[col_name] = {
                        'type': 'categorical',
                        'selected': selected
                    }
        
        elif filter_type == 'numeric':
            min_val = filter_config.get('min', 0)
            max_val = filter_config.get('max', 100)
            
            range_values = st.sidebar.slider(
                f"Range:",
                min_value=float(min_val),
                max_value=float(max_val),
                value=(float(min_val), float(max_val)),
                key=f"{key_prefix}_{col_name}_range",
                help=f"Filter {col_name} by value range"
            )
            
            if range_values[0] != min_val or range_values[1] != max_val:
                filters[col_name] = {
                    'type': 'numeric',
                    'min': range_values[0],
                    'max': range_values[1]
                }
        
        elif filter_type == 'date':
            min_date = filter_config.get('min')
            max_date = filter_config.get('max')
            
            if min_date and max_date:
                date_range = st.sidebar.date_input(
                    f"Date range:",
                    value=(pd.to_datetime(min_date).date(), pd.to_datetime(max_date).date()),
                    min_value=pd.to_datetime(min_date).date(),
                    max_value=pd.to_datetime(max_date).date(),
                    key=f"{key_prefix}_{col_name}_date_range",
                    help=f"Filter {col_name} by date range"
                )
                
                if len(date_range) == 2:
                    filters[col_name] = {
                        'type': 'date',
                        'min': date_range[0].isoformat(),
                        'max': date_range[1].isoformat()
                    }
        
        st.sidebar.markdown("---")
    
    return filters

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 ETL Data Processing Tool</h1>', unsafe_allow_html=True)
    st.markdown("Upload CSV or Excel files, clean your data, apply filters, and perform joins across sheets.")
    
    # Check API connection
    if not check_api_connection():
        st.error("⚠️ Cannot connect to the API server. Please make sure the FastAPI backend is running on http://localhost:8000")
        st.info("To start the backend, run: `uvicorn backend.main:app --reload` from the project root directory")
        st.stop()
    
    # Initialize session state
    if 'file_data' not in st.session_state:
        st.session_state.file_data = None
    if 'current_sheet' not in st.session_state:
        st.session_state.current_sheet = None
    if 'filtered_data' not in st.session_state:
        st.session_state.filtered_data = None
    if 'available_sheets' not in st.session_state:
        st.session_state.available_sheets = []
    
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        
        # File upload section
        st.header("📁 Upload File")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a CSV or Excel file to start processing"
        )
        
        if uploaded_file is not None:
            if st.button("Process File", type="primary"):
                with st.spinner("Processing file..."):
                    result = upload_file_to_api(uploaded_file)
                    
                    if result:
                        st.session_state.file_data = result
                        metadata = result['metadata']
                        st.session_state.available_sheets = list(metadata['sheets'].keys())
                        st.success("✅ File processed successfully!")
                        st.rerun()
        
        # Sheet selection
        if st.session_state.file_data:
            st.header("📊 Select Sheet")
            sheets = st.session_state.available_sheets
            
            selected_sheet = st.selectbox(
                "Choose a sheet:",
                sheets,
                key="sheet_selector"
            )
            
            if selected_sheet != st.session_state.current_sheet:
                st.session_state.current_sheet = selected_sheet
                st.session_state.filtered_data = None  # Reset filtered data
                st.rerun()
    
    # Main content area
    if st.session_state.file_data is None:
        # Welcome screen
        st.info("👆 Please upload a CSV or Excel file using the sidebar to get started.")
        
        # Show supported features
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🧹 Data Cleaning
            - Remove duplicates
            - Handle missing values
            - Data type conversion
            - Text normalization
            """)
        
        with col2:
            st.markdown("""
            ### 🔍 Filtering
            - Categorical filters
            - Numeric range filters
            - Date range filters
            - Multiple column filtering
            """)
        
        with col3:
            st.markdown("""
            ### 🔗 Data Joining
            - Inner/Left/Right/Outer joins
            - Auto-detect common keys
            - Join validation
            - Export results
            """)
        
        return
    
    # Main processing area
    file_id = st.session_state.file_data['file_id']
    metadata = st.session_state.file_data['metadata']
    
    # File information header
    st.markdown(f"""
    <div class="success-message">
    📄 <strong>File:</strong> {metadata['filename']} | 
    <strong>Type:</strong> {metadata['file_type']} | 
    <strong>Sheets:</strong> {len(metadata['sheets'])} |
    <strong>Upload Time:</strong> {pd.to_datetime(metadata['upload_time']).strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.current_sheet:
        selected_sheet = st.session_state.current_sheet
        sheet_metadata = metadata['sheets'][selected_sheet]
        
        # Add filters to sidebar if sheet is selected
        with st.sidebar:
            if sheet_metadata.get('filters'):
                filters = render_filters_sidebar(sheet_metadata, f"filter_{selected_sheet}")
                
                if st.button("Apply Filters", type="secondary"):
                    if filters:
                        with st.spinner("Applying filters..."):
                            filtered_response = apply_filters_api(file_id, selected_sheet, filters)
                            
                            if filtered_response:
                                st.session_state.filtered_data = filtered_response
                                st.success(f"✅ Filters applied!")
                                st.rerun()
                    else:
                        st.warning("No filters selected")
                
                if st.button("Clear Filters", type="secondary"):
                    st.session_state.filtered_data = None
                    st.rerun()
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Data View", "🔗 Join Sheets", "📊 Data Insights", "💾 Export"])
        
        with tab1:
            st.header(f"Data: {selected_sheet}")
            
            # Show filtered data if available, otherwise show original data
            display_data = st.session_state.filtered_data
            if display_data is None:
                with st.spinner("Loading data..."):
                    display_data = get_data_from_api(file_id, selected_sheet, limit=1000)
            
            if display_data:
                # Show filter status
                if st.session_state.filtered_data:
                    st.info(f"🔍 Showing filtered data: {display_data['filtered_rows']} of {display_data['total_rows']} rows")
                else:
                    st.info(f"📊 Showing original data: {display_data['total_rows']} rows")
                
                render_data_overview(display_data, selected_sheet)
        
        with tab2:
            st.header("Join Sheets")
            
            sheets = list(metadata['sheets'].keys())
            if len(sheets) > 1:
                # Show suggested joins
                common_keys = metadata.get('common_keys', [])
                if common_keys:
                    st.subheader("🎯 Suggested Joins")
                    for i, key_info in enumerate(common_keys[:3]):
                        with st.expander(f"Join {key_info['sheet1']} ↔ {key_info['sheet2']} on '{key_info['column']}'"):
                            st.write(f"**Common Column:** {key_info['column']}")
                            st.write(f"**Matching Values:** {key_info['overlap_count']}")
                            
                            join_type = st.selectbox(
                                "Join Type:",
                                ["inner", "left", "right", "outer"],
                                key=f"suggested_join_type_{i}",
                                help="Choose how to combine the datasets"
                            )
                            
                            if st.button(f"Perform Join", key=f"suggested_join_{i}", type="primary"):
                                with st.spinner("Joining sheets..."):
                                    join_response = join_sheets_api(
                                        file_id, key_info['sheet1'], key_info['sheet2'], 
                                        key_info['column'], key_info['column'], join_type
                                    )
                                    
                                    if join_response:
                                        # Add the new joined sheet to available sheets
                                        st.session_state.available_sheets.append(join_response['joined_sheet_name'])
                                        st.success(f"✅ Sheets joined! New sheet: {join_response['joined_sheet_name']}")
                                        
                                        # Preview joined data
                                        st.subheader("Preview of Joined Data")
                                        joined_df = pd.DataFrame(join_response['data'])
                                        st.dataframe(joined_df, use_container_width=True)
                                        st.info(f"Total rows in joined data: {join_response['total_rows']}")
                
                st.markdown("---")
                
                # Manual join configuration
                st.subheader("🔧 Manual Join Configuration")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Left Dataset**")
                    left_sheet = st.selectbox("Select left sheet:", sheets, key="manual_left_sheet")
                    if left_sheet:
                        left_columns = metadata['sheets'][left_sheet]['column_names']
                        left_key = st.selectbox("Select join key:", left_columns, key="manual_left_key")
                
                with col2:
                    st.write("**Right Dataset**")
                    available_right_sheets = [s for s in sheets if s != left_sheet] if 'left_sheet' in locals() else sheets
                    right_sheet = st.selectbox("Select right sheet:", available_right_sheets, key="manual_right_sheet")
                    if right_sheet:
                        right_columns = metadata['sheets'][right_sheet]['column_names']
                        right_key = st.selectbox("Select join key:", right_columns, key="manual_right_key")
                
                join_type = st.selectbox(
                    "Join Type:",
                    ["inner", "left", "right", "outer"],
                    key="manual_join_type",
                    help="Inner: Only matching rows | Left: All left + matching right | Right: All right + matching left | Outer: All rows"
                )
                
                if st.button("Perform Manual Join", type="primary"):
                    if 'left_sheet' in locals() and 'right_sheet' in locals() and 'left_key' in locals() and 'right_key' in locals():
                        with st.spinner("Joining sheets..."):
                            join_response = join_sheets_api(file_id, left_sheet, right_sheet, left_key, right_key, join_type)
                            
                            if join_response:
                                st.session_state.available_sheets.append(join_response['joined_sheet_name'])
                                st.success(f"✅ Manual join completed! New sheet: {join_response['joined_sheet_name']}")
                                
                                # Preview
                                st.subheader("Preview of Joined Data")
                                joined_df = pd.DataFrame(join_response['data'])
                                st.dataframe(joined_df, use_container_width=True)
                    else:
                        st.error("Please select all required fields for joining")
            else:
                st.info("Upload a file with multiple sheets to perform joins")
        
        with tab3:
            st.header("Data Insights")
            
            # Load data for insights
            with st.spinner("Generating insights..."):
                insight_data = get_data_from_api(file_id, selected_sheet, limit=5000)
            
            if insight_data:
                df = pd.DataFrame(insight_data['data'])
                
                if not df.empty:
                    # Column analysis
                    st.subheader("📊 Column Analysis")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Data types distribution
                        type_counts = df.dtypes.value_counts()
                        fig = px.pie(values=type_counts.values, names=type_counts.index, 
                                   title="Data Types Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Missing values analysis
                        missing_data = df.isnull().sum()
                        missing_data = missing_data[missing_data > 0]
                        
                        if not missing_data.empty:
                            fig = px.bar(x=missing_data.index, y=missing_data.values,
                                       title="Missing Values by Column")
                            fig.update_layout(xaxis_title="Columns", yaxis_title="Missing Count")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.success("🎉 No missing values found!")
                    
                    # Numeric columns correlation
                    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                    if len(numeric_cols) > 1:
                        st.subheader("🔗 Correlation Matrix")
                        corr_matrix = df[numeric_cols].corr()
                        
                        fig = px.imshow(corr_matrix, 
                                      title="Correlation Matrix of Numeric Columns",
                                      color_continuous_scale="RdBu")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Summary statistics
                    st.subheader("📈 Summary Statistics")
                    if len(numeric_cols) > 0:
                        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                    else:
                        st.info("No numeric columns available for statistical summary")
                    
                    df = sanitize_dataframe_for_plot(df)
                    fig = px.histogram(df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
                    st.plotly_chart(fig, use_container_width=True)

        
        with tab4:
            st.header("Export Data")
            
            # Available sheets for download
            available_sheets_for_download = st.session_state.available_sheets
            
            selected_download_sheet = st.selectbox(
                "Select sheet to download:",
                available_sheets_for_download,
                key="download_sheet_selector"
            )
            
            if selected_download_sheet:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📥 Download as CSV", type="primary"):
                        with st.spinner("Preparing download..."):
                            csv_data = download_data_from_api(file_id, selected_download_sheet)
                            
                            if csv_data:
                                st.download_button(
                                    label="💾 Download CSV File",
                                    data=csv_data,
                                    file_name=f"{selected_download_sheet}_processed.csv",
                                    mime="text/csv"
                                )
                                st.success("✅ File ready for download!")
                
                with col2:
                    # Show download preview
                    with st.spinner("Loading preview..."):
                        preview_data = get_data_from_api(file_id, selected_download_sheet, limit=5)
                        
                        if preview_data:
                            st.write("**Download Preview:**")
                            preview_df = pd.DataFrame(preview_data['data'])
                            st.dataframe(preview_df, use_container_width=True)
                            st.info(f"Total rows to download: {preview_data['total_rows']}")
            
            # Bulk download option
            if len(available_sheets_for_download) > 1:
                st.markdown("---")
                st.subheader("📦 Bulk Download")
                
                if st.button("Download All Sheets", type="secondary"):
                    st.info("💡 Feature coming soon! For now, please download sheets individually.")

if __name__ == "__main__":
    main()