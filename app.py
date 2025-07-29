# app.py
import streamlit as st
from file_handler import load_file, get_sheet_names, preview_sheets
from cleaning import clean_master_yazaki, clean_generic_sheet
from preprocessing import suggest_column, add_activation_status


st.set_page_config(page_title="ETL Automation Tool", layout="wide")

# Initialize session state for logs
if 'logs' not in st.session_state:
    st.session_state.logs = []

def add_log(message):
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")

# Create main layout with two sidebars
with st.sidebar:
    st.title("Upload Files")
    
    # Clear All button
    if st.button("🗑️ Clear All", type="secondary"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.session_state.logs = []
        st.toast("Application state cleared. Reloading...", icon="🔄")
        st.rerun()
        #st.session_state.clear()
        #st.session_state.logs = []
        #add_log("Application cleared")
        #st.rerun()
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])

# Activity Logs in a separate sidebar using columns
col_main, col_logs = st.columns([4, 1])

with col_logs:
    st.subheader("📋 Activity Logs")
    if st.session_state.logs:
        for log in reversed(st.session_state.logs[-15:]):  # Show last 15 logs
            st.text(log)
    else:
        st.text("No activity yet...")
    
    if st.button("Clear Logs"):
        st.session_state.logs = []
        st.rerun()

with col_main:
    if uploaded_file:
        add_log(f"File uploaded: {uploaded_file.name}")
        # Load sheets
        sheets = load_file(uploaded_file)
        sheet_names = get_sheet_names(sheets)
        add_log(f"Loaded {len(sheet_names)} sheets")

        # Select MasterBOM sheet
        st.sidebar.subheader("Select Master BOM Sheet")
        master_sheet = st.sidebar.selectbox("MasterBOM", sheet_names)

        # Select target sheet
        st.sidebar.subheader("Select Target Sheet")
        target_sheet = st.sidebar.selectbox("Sheet to Process", [s for s in sheet_names if s != master_sheet])

        # Preview raw data
        st.header("Preview Raw Data")
        preview_sheets(sheets, [master_sheet, target_sheet])

        # Cleaning
        st.header("Cleaning Phase")
        # Master BOM cleaning: only clean YAZAKI PN col
        master_df = sheets[master_sheet].copy()
        st.write(f"**DEBUG:** Master before cleaning - Shape: {master_df.shape}")
        master_df = clean_master_yazaki(master_df)
        st.write(f"**DEBUG:** Master after cleaning - Shape: {master_df.shape}")
        st.subheader(f"Cleaned Master ({master_sheet}) — YAZAKI PN only")
        st.dataframe(master_df[["YAZAKI PN"]].head(5))
        
        # Generic cleaning for target
        target_df = sheets[target_sheet].copy()
        st.write(f"**DEBUG:** Target before cleaning - Shape: {target_df.shape}")
        target_df = clean_generic_sheet(target_df)
        st.write(f"**DEBUG:** Target after cleaning - Shape: {target_df.shape}")
        
        # Ensure YAZAKI PN is first column and rename properly
        cols = list(target_df.columns)
        st.write(f"**DEBUG:** Target columns after cleaning: {cols[:5]}...")
        if "YAZAKI_PN" in cols:
            target_df.rename(columns={"YAZAKI_PN": "YAZAKI PN"}, inplace=True)
            cols = list(target_df.columns)
            cols.insert(0, cols.pop(cols.index("YAZAKI PN")))
            target_df = target_df[cols]
            st.write(f"**DEBUG:** Target columns after reordering: {list(target_df.columns)[:5]}...")
        st.subheader(f"Cleaned Target ({target_sheet})")
        st.dataframe(target_df.head(5))

        # Preprocessing / Lockup
        st.header("Preprocessing & LOCKUP")
        st.write("**Key column**: YAZAKI PN (default)")

        # Choose lookup column from Master (cols 2–22)
        permissible = list(master_df.columns)[1:22]
        user_input = st.text_input("Enter column to return from Master sheet:")
        suggestion = suggest_column(user_input, permissible)
        st.write(f"Suggested: **{suggestion}**")
        lookup_col = st.selectbox("Select return column", permissible, index=permissible.index(suggestion) if suggestion in permissible else 0)

        # Activate LOCKUP
        if st.button("LOCKUP"):
            # Debug info before lookup
            st.write("**Debug Info:**")
            st.write(f"Master records: {len(master_df)}")
            st.write(f"Target records: {len(target_df)}")
            st.write(f"Master //unique YAZAKI PN: {master_df['YAZAKI PN']}")
            st.write(f"Target //unique YAZAKI PN: {target_df['YAZAKI PN']}")
            
            result = add_activation_status(
                master_df, target_df, key_col="YAZAKI PN", lookup_col=lookup_col
            )
            st.subheader("Result with Activation Status")
            st.dataframe(result.head(20))
            
            # KPI Section
            st.subheader("Activation Status KPIs")
            kpi_counts = result['ACTIVATION_STATUS'].value_counts()
            na_count = result['ACTIVATION_STATUS'].isna().sum()
            total_records = len(result)
            
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
                            
            # Override target sheet with processed result
            sheets[target_sheet] = result.copy()
            add_log(f"Target sheet '{target_sheet}' updated with ACTIVATION_STATUS")
            st.success(f"✅ Sheet '{target_sheet}' has been updated with activation status")
            
            # Download button for complete processed data
            st.download_button(
                label="📥 Download Complete Processed Data",
                data=result.to_csv(index=False).encode("utf-8"),
                file_name=f"processed_{target_sheet}.csv",
                mime="text/csv",
                help="Downloads the entire processed dataset, not just the preview shown above"
            )
            
            
