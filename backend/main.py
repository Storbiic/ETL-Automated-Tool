from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Dict
import logging
from datetime import datetime
import uuid

from .services.etl import ETLService

from .models.schema import FilterRequest, JoinRequest, UploadResponse, DataResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ETL Data Processing API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ETL service
etl_service = ETLService()

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file"""
    try:
        file_id = str(uuid.uuid4())
        result = await etl_service.process_uploaded_file(file, file_id)
        return result
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/data/{file_id}/{sheet_name}", response_model=DataResponse)
async def get_data(file_id: str, sheet_name: str, limit: int = 100):
    """Get data from a specific sheet"""
    try:
        result = etl_service.get_sheet_data(file_id, sheet_name, limit)
        return result
    except Exception as e:
        logger.error(f"Error getting data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/filter")
async def apply_filters(request: FilterRequest):
    """Apply filters to data"""
    try:
        result = etl_service.apply_filters(request)
        return result
    except Exception as e:
        logger.error(f"Error applying filters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/join")
async def join_sheets(request: JoinRequest):
    """Join two sheets on specified keys"""
    try:
        result = etl_service.join_sheets(request)
        return result
    except Exception as e:
        logger.error(f"Error joining sheets: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/download/{file_id}/{sheet_name}")
async def download_data(file_id: str, sheet_name: str):
    """Download processed data as CSV"""
    try:
        response = etl_service.download_csv(file_id, sheet_name)
        return response
    except Exception as e:
        logger.error(f"Error downloading data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/metadata/{file_id}")
async def get_metadata(file_id: str):
    """Get file metadata"""
    try:
        result = etl_service.get_metadata(file_id)
        return result
    except Exception as e:
        logger.error(f"Error getting metadata: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/data/{file_id}")
async def delete_data(file_id: str):
    """Delete stored data"""
    try:
        etl_service.delete_data(file_id)
        return {"message": "Data deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)