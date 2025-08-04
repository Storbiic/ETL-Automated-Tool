# ETL Tool v2.0 - Technical Backup

## 🔧 Core Configuration

### Backend Main Configuration (backend/main.py)
- FastAPI application with CORS enabled
- File upload endpoint with validation
- Sheet preview functionality
- Data cleaning pipeline
- LOCKUP processing
- Master BOM update logic

### Frontend Configuration (frontend/app.py)
- Streamlit page config with wide layout
- 6-step workflow implementation
- Progress tracking with session state
- Enhanced UI with custom CSS
- Real-time activity logging

## 📊 Data Processing Pipeline

### Step 1: File Upload
- Supports Excel (.xlsx, .xls) and CSV files
- Automatic file validation and parsing
- Sheet detection and preview generation

### Step 2: Data Preview & Sheet Selection
- Interactive sheet selection
- Data preview with first 10 rows
- Column detection and validation

### Step 3: Data Cleaning
- Master BOM: YAZAKI PN standardization
- Target Sheet: Column standardization and cleaning
- Automatic data type detection and conversion

### Step 4: LOCKUP Configuration
- Column mapping between Master and Target
- Lookup dictionary creation
- Activation status assignment (X, D, 0, NOT_FOUND)

### Step 5: Results Visualization
- Bar charts showing status distribution
- Searchable data tables
- Statistical summaries

### Step 6: Master BOM Updates
- Status-based update logic
- Duplicate detection and handling
- Record insertion and modification
- Comprehensive logging

## 🔄 Master BOM Update Logic

### Status Processing:
1. **'X' Status**: Records are skipped (no changes)
2. **'D' Status**: Update existing records, then change D→X
3. **'0' Status**: Check for duplicates, insert if unique
4. **'NOT_FOUND'**: Insert as new records

### Key Functions:
- `_update_existing_records()`: Handles D status updates
- `_handle_zero_status()`: Manages duplicate checking
- `_insert_new_records()`: Processes new record insertion
- `_prepare_new_record()`: Creates properly formatted records

## 🎨 UI Components

### Enhanced Features:
- Custom CSS styling for professional appearance
- Progress bars with step indicators
- Activity logs in sidebar
- Search functionality instead of pagination
- Bar charts for better data visualization
- Success/error message handling

### Key Components:
- `display_dataframe_with_search()`: Enhanced data tables
- `create_status_chart()`: Bar chart generation
- `display_kpi_metrics()`: Statistical displays
- `create_progress_bar()`: Visual progress tracking

## 🔍 Search and Filtering

### Implementation:
- Real-time search across all data columns
- Case-insensitive matching
- Instant results without page refresh
- Maintains data integrity during filtering

## 📈 Visualization

### Chart Types:
- Bar charts for activation status distribution
- KPI metrics for data summaries
- Progress indicators for workflow steps

### Libraries Used:
- Plotly Express for interactive charts
- Streamlit native components for metrics
- Custom CSS for enhanced styling

## 🛡 Error Handling

### Comprehensive Coverage:
- File upload validation
- Data format checking
- API communication error handling
- User-friendly error messages
- Graceful degradation on failures

## 📝 Logging System

### Features:
- Timestamped activity logs
- Real-time updates in sidebar
- Operation tracking throughout workflow
- Debug information for troubleshooting

## 🔧 Technical Dependencies

### Backend:
- FastAPI: Web framework
- uvicorn: ASGI server
- pandas: Data processing
- openpyxl: Excel file handling
- pydantic: Data validation

### Frontend:
- streamlit: Web interface
- plotly: Data visualization
- requests: API communication
- pandas: Data manipulation

## 🚀 Deployment Configuration

### Development Setup:
- Backend: uvicorn with auto-reload
- Frontend: Streamlit with custom port
- CORS enabled for local development
- Debug logging available

### Production Ready:
- Proper error handling
- Input validation
- Secure file handling
- Performance optimizations

This technical backup ensures all implementation details are preserved
for the working version of the ETL Automation Tool v2.0.
