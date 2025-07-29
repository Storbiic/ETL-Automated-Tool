"""
FastAPI backend for ETL Automation Tool
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import logging
from typing import List

from .models import (
    FileUploadResponse, SheetPreviewRequest, SheetPreviewResponse,
    CleaningRequest, CleaningResponse, LookupRequest, LookupResponse,
    ColumnSuggestionRequest, ColumnSuggestionResponse, MasterUpdateRequest,
    MasterUpdateResponse, ErrorResponse
)
from .core.file_handler import file_manager
from .core.cleaning import data_cleaner
from .core.preprocessing import data_processor
from .core.master_updater import master_updater

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ETL Automation Tool API",
    description="Backend API for ETL data processing and automation",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ETL Automation Tool API is running", "version": "2.0.0"}


@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a CSV or Excel file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.csv', '.xls', '.xlsx')):
            raise HTTPException(
                status_code=400, 
                detail="Only CSV and Excel files are supported"
            )
        
        # Read file content
        content = await file.read()
        
        # Save file and get ID
        file_id = file_manager.save_uploaded_file(content, file.filename)
        
        # Get sheet names
        sheet_names = file_manager.get_sheet_names(file_id)
        
        logger.info(f"File uploaded successfully: {file.filename}, ID: {file_id}")
        
        return FileUploadResponse(
            success=True,
            message=f"File '{file.filename}' uploaded successfully",
            sheet_names=sheet_names,
            file_id=file_id
        )
        
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/preview", response_model=SheetPreviewResponse)
async def preview_sheets(request: SheetPreviewRequest):
    """Get preview of specified sheets"""
    try:
        previews = file_manager.preview_sheets(request.file_id, request.sheet_names)
        
        return SheetPreviewResponse(
            success=True,
            previews=previews
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Preview failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clean", response_model=CleaningResponse)
async def clean_data(request: CleaningRequest):
    """Clean master and target sheets"""
    try:
        # Get original sheets
        master_df = file_manager.get_sheet(request.file_id, request.master_sheet)
        target_df = file_manager.get_sheet(request.file_id, request.target_sheet)
        
        # Clean master sheet (YAZAKI PN only)
        master_cleaned, master_stats = data_cleaner.clean_master_yazaki(master_df)
        
        # Clean target sheet
        target_cleaned, target_stats = data_cleaner.clean_generic_sheet(target_df)
        target_cleaned = data_cleaner.prepare_target_sheet(target_cleaned)
        
        # Store cleaned data
        file_manager.update_sheet(request.file_id, request.master_sheet, master_cleaned)
        file_manager.update_sheet(request.file_id, request.target_sheet, target_cleaned)
        
        return CleaningResponse(
            success=True,
            message="Data cleaning completed successfully",
            master_preview=master_cleaned[["YAZAKI PN"]].head(5).to_dict('records'),
            target_preview=target_cleaned.head(5).to_dict('records'),
            master_shape=list(master_cleaned.shape),
            target_shape=list(target_cleaned.shape)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Cleaning failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggest-column", response_model=ColumnSuggestionResponse)
async def suggest_column(request: ColumnSuggestionRequest):
    """Suggest best matching column from available options"""
    try:
        suggested, confidence = data_processor.suggest_column(
            request.input_name,
            request.available_columns
        )

        return ColumnSuggestionResponse(
            suggested_column=suggested,
            confidence=confidence
        )

    except Exception as e:
        logger.error(f"Column suggestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/columns/{file_id}/{sheet_name}")
async def get_lookup_columns(file_id: str, sheet_name: str):
    """Get available columns for lookup from master sheet"""
    try:
        master_df = file_manager.get_processed_sheet(file_id, sheet_name)
        columns = data_processor.get_column_suggestions(master_df)

        return {"success": True, "columns": columns}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Get columns failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lookup", response_model=LookupResponse)
async def perform_lookup(request: LookupRequest):
    """Perform lookup operation and add activation status"""
    try:
        # Get cleaned sheets
        master_df = file_manager.get_processed_sheet(request.file_id, request.master_sheet)
        target_df = file_manager.get_processed_sheet(request.file_id, request.target_sheet)

        # Perform lookup
        result_df, stats = data_processor.add_activation_status(
            master_df, target_df, request.key_column, request.lookup_column
        )

        # Store result
        file_manager.update_sheet(request.file_id, request.target_sheet, result_df)

        # Generate download URL (simplified for demo)
        download_url = f"/download/{request.file_id}/{request.target_sheet}"

        return LookupResponse(
            success=True,
            message="Lookup completed successfully",
            result_preview=result_df.head(20).to_dict('records'),
            kpi_counts=stats["mapping_results"],
            total_records=stats["total_processed"],
            download_url=download_url
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Lookup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{file_id}/{sheet_name}")
async def download_processed_data(file_id: str, sheet_name: str):
    """Download processed data as CSV"""
    try:
        df = file_manager.get_processed_sheet(file_id, sheet_name)

        # Create CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=processed_{sheet_name}.csv"}
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-updates", response_model=MasterUpdateResponse)
async def process_master_updates(request: MasterUpdateRequest):
    """Process Master BOM updates based on activation status"""
    try:
        # Get processed sheets
        master_df = file_manager.get_processed_sheet(request.file_id, request.master_sheet)
        target_df = file_manager.get_processed_sheet(request.file_id, request.target_sheet)

        # Process updates
        updated_master, stats = master_updater.process_updates(
            master_df, target_df, request.lookup_column
        )

        # Store updated master
        file_manager.update_sheet(request.file_id, request.master_sheet, updated_master)

        return MasterUpdateResponse(
            success=True,
            message="Master BOM updates completed successfully",
            updated_count=stats["updated_count"],
            inserted_count=stats["inserted_count"],
            duplicates_count=stats["duplicates_count"],
            skipped_count=stats["skipped_count"],
            duplicates=stats["duplicates"]
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Master BOM update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
