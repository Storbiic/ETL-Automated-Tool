# ETL Automation Tool v2.0

A modern, professional ETL (Extract, Transform, Load) automation tool built with FastAPI backend and Streamlit frontend for processing YAZAKI data files.

## 🚀 Features

- **Modern Architecture**: Separated backend (FastAPI) and frontend (Streamlit) for better maintainability
- **Enhanced UI**: Improved user experience with progress tracking, better visualizations, and responsive design
- **Robust Data Processing**: Advanced data cleaning, validation, and lookup operations
- **Real-time Feedback**: Live activity logs and progress indicators
- **Professional APIs**: RESTful API endpoints with proper validation and error handling
- **File Support**: CSV and Excel file processing with multiple sheet support
- **Data Visualization**: Interactive charts and KPI dashboards
- **Download Capabilities**: Export processed data in CSV format

## 📁 Project Structure

```
etl_app/
├── backend/                 # FastAPI backend
│   ├── __init__.py
│   ├── main.py             # FastAPI application
│   ├── models.py           # Pydantic models
│   ├── config.py           # Configuration settings
│   └── core/               # Core business logic
│       ├── __init__.py
│       ├── file_handler.py # File management
│       ├── cleaning.py     # Data cleaning
│       └── preprocessing.py # Data processing
├── frontend/               # Streamlit frontend
│   ├── __init__.py
│   ├── app.py             # Main Streamlit app
│   ├── api_client.py      # API communication
│   └── components.py      # UI components
├── uploads/               # File upload directory
├── requirements.txt       # Python dependencies
├── run_app.py            # Main application runner
├── start_backend.py      # Backend startup script
├── start_frontend.py     # Frontend startup script
└── README.md             # This file
```

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:Storbiic/ETL_Automated_Tool.git
   cd etl_app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Option 1: Run Both Services Together (Recommended)
```bash
python run_app.py
```

### Option 2: Run Services Separately

**Terminal 1 - Backend:**
```bash
python start_backend.py
```

**Terminal 2 - Frontend:**
```bash
python start_frontend.py
```

### Option 3: Manual Startup

**Backend:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
streamlit run app.py --server.port 8501
```

## 🌐 Access Points

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage Guide

### 1. File Upload
- Upload CSV or Excel files through the web interface
- Supports multiple sheet Excel files
- Files are automatically validated and processed

### 2. Sheet Selection
- Preview uploaded data
- Select Master BOM sheet and Target sheet for processing
- View data structure and content before processing

### 3. Data Cleaning
- Automatic data standardization and cleaning
- YAZAKI PN column normalization
- Generic sheet formatting and preparation

### 4. Lookup Configuration
- Select lookup columns from Master sheet
- Intelligent column suggestion based on input
- Configure lookup parameters

### 5. Data Processing
- Perform lookup operations with activation status
- View real-time processing statistics
- Generate comprehensive KPI reports

### 6. Results & Export
- Interactive data visualization
- Detailed KPI metrics and charts
- Export processed data as CSV

## 🔧 API Endpoints

- `POST /upload` - Upload files
- `POST /preview` - Preview sheet data
- `POST /clean` - Clean data
- `POST /suggest-column` - Get column suggestions
- `GET /columns/{file_id}/{sheet_name}` - Get available columns
- `POST /lookup` - Perform lookup operations
- `GET /download/{file_id}/{sheet_name}` - Download processed data

## 🧪 Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8 .
```

## 📝 Configuration

Environment variables can be set in a `.env` file:

```env
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
MAX_FILE_SIZE=104857600
UPLOAD_DIR=uploads
LOG_LEVEL=INFO
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at http://localhost:8000/docs
2. Review the activity logs in the application
3. Check the console output for detailed error messages

## 🔄 Migration from v1.0

The new architecture maintains full compatibility with existing functionality while providing:
- Better separation of concerns
- Improved error handling
- Enhanced user experience
- Professional API design
- Better maintainability and extensibility
