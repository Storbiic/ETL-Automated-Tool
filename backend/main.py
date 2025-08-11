"""
FastAPI backend for ETL Automation Tool
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import os
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

from .config import settings
from .models import (
    FileUploadResponse, SheetPreviewRequest, SheetPreviewResponse,
    CleaningRequest, CleaningResponse, LookupRequest, LookupResponse,
    ColumnSuggestionRequest, ColumnSuggestionResponse, MasterUpdateRequest,
    MasterUpdateResponse, SharePointConfigRequest, SharePointFileListResponse,
    SharePointDownloadRequest, SharePointDownloadResponse, SharePointUploadRequest,
    SharePointUploadResponse, SharePointRollbackRequest, SharePointRollbackResponse,
    ProcessingPreviewRequest, ProcessingPreviewResponse, ErrorResponse
)
from .core.file_handler import file_manager
from .core.cleaning import data_cleaner
from .core.preprocessing import data_processor
from .core.master_updater import master_updater
from .core.log_manager import log_manager, setup_log_capture

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup log capture for export functionality
setup_log_capture()

# Simple session storage (in production, use Redis or database)
session_storage = {}

def rebuild_session_storage():
    """Rebuild session storage from file_manager data"""
    global session_storage
    session_storage.clear()

    for file_id, file_data in file_manager.files_storage.items():
        session_storage[file_id] = {
            'file_id': file_id,
            'filename': file_data['filename'],
            'sheet_names': list(file_data['sheets'].keys()),
            'master_sheet': None,
            'target_sheet': None
        }

    logger.info(f"Rebuilt session storage with {len(session_storage)} files")

def get_session_data():
    """Get the most recent session data"""
    if not session_storage:
        rebuild_session_storage()

    if not session_storage:
        return {}

    # Get the most recent file_id
    file_id = list(session_storage.keys())[-1]
    session_data = session_storage[file_id]

    # Add file path for dashboard endpoints
    if file_id in file_manager.files_storage:
        file_data = file_manager.files_storage[file_id]
        session_data['file_path'] = file_data.get('file_path')

    return session_data

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],  # Include configured origins plus wildcard for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ETL Automation Tool API is running", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "healthy",
        "message": "ETL API is running",
        "version": "2.0",
        "timestamp": datetime.now().isoformat()
    }


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

        # Store in session for React frontend compatibility
        session_storage[file_id] = {
            'file_id': file_id,
            'filename': file.filename,
            'sheet_names': sheet_names,
            'master_sheet': None,
            'target_sheet': None
        }

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
        # Also store as processed master for SharePoint upload
        file_manager.files_storage[request.file_id]["processed_master"] = updated_master

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



@app.post("/sharepoint/list-files", response_model=SharePointFileListResponse)
async def list_sharepoint_files(request: SharePointConfigRequest):
    """List files in SharePoint folder"""
    try:
        from .core.sharepoint_client import SharePointClient

        client = SharePointClient(request.site_url, request.username, request.password)

        if not client.authenticate():
            raise HTTPException(status_code=401, detail="SharePoint authentication failed")

        files = client.list_files(request.folder_path)

        return SharePointFileListResponse(
            success=True,
            message=f"Found {len(files)} files in SharePoint folder",
            files=files
        )

    except Exception as e:
        logger.error(f"SharePoint file listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sharepoint/download", response_model=SharePointDownloadResponse)
async def download_sharepoint_file(request: SharePointDownloadRequest):
    """Download file from SharePoint and make it available for ETL processing"""
    try:
        from .core.sharepoint_client import SharePointClient
        import tempfile
        import uuid

        client = SharePointClient(request.site_url, request.username, request.password)

        if not client.authenticate():
            raise HTTPException(status_code=401, detail="SharePoint authentication failed")

        # Create backup first
        backup_name = client.create_backup(request.folder_path, request.file_name)
        if backup_name:
            logger.info(f"🛡️ Backup created: {backup_name}")

        # Download file to temporary location
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, request.file_name)

        if client.download_file(request.folder_path, request.file_name, temp_file):
            # Generate file ID and store in file manager
            file_id = str(uuid.uuid4())

            # Read file and store in file manager
            if request.file_name.endswith('.xlsx') or request.file_name.endswith('.xls'):
                sheets_data = pd.read_excel(temp_file, sheet_name=None)
            elif request.file_name.endswith('.csv'):
                df = pd.read_csv(temp_file)
                sheets_data = {"Sheet1": df}
            else:
                raise ValueError("Unsupported file format")

            # Store in file manager
            file_manager.files_storage[file_id] = {
                "filename": request.file_name,
                "sheets": sheets_data,
                "processed_sheets": {},
                "source": "sharepoint"
            }

            # Cleanup temp file
            os.remove(temp_file)
            os.rmdir(temp_dir)

            logger.info(f"SharePoint file downloaded and processed: {request.file_name}, ID: {file_id}")

            return SharePointDownloadResponse(
                success=True,
                message=f"File '{request.file_name}' downloaded from SharePoint successfully",
                file_id=file_id,
                file_name=request.file_name
            )
        else:
            raise Exception("Failed to download file from SharePoint")

    except Exception as e:
        logger.error(f"SharePoint download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/processing/preview", response_model=ProcessingPreviewResponse)
async def preview_processing_changes(request: ProcessingPreviewRequest):
    """Preview changes before applying them to Master BOM"""
    try:
        from .core.processing_preview import ProcessingPreview

        # Get the data
        master_df = file_manager.get_sheet(request.file_id, request.master_sheet)
        target_df = file_manager.get_sheet(request.file_id, request.target_sheet)

        # Generate preview
        preview_data = ProcessingPreview.generate_preview(
            master_df, target_df, request.lookup_column, request.key_column
        )

        return ProcessingPreviewResponse(
            success=True,
            message="Processing preview generated successfully",
            changes_summary=preview_data["changes_summary"],
            updated_records_preview=preview_data["updated_records_preview"],
            inserted_records_preview=preview_data["inserted_records_preview"],
            duplicates_preview=preview_data["duplicates_preview"],
            statistics=preview_data["statistics"]
        )

    except Exception as e:
        logger.error(f"Processing preview failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sharepoint/upload", response_model=SharePointUploadResponse)
async def upload_to_sharepoint(request: SharePointUploadRequest):
    """Upload processed file back to SharePoint with backup"""
    try:
        from .core.sharepoint_client import SharePointClient
        import tempfile

        client = SharePointClient(request.site_url, request.username, request.password)

        if not client.authenticate():
            raise HTTPException(status_code=401, detail="SharePoint authentication failed")

        # Get the processed file from file manager
        if request.file_id not in file_manager.files_storage:
            raise HTTPException(status_code=404, detail="File not found")

        file_data = file_manager.files_storage[request.file_id]

        # Create temporary file with processed data
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, request.file_name)

        # Save the processed data to temporary file
        if 'processed_master' in file_data:
            # Use processed master data
            file_data['processed_master'].to_excel(temp_file, index=False)
        else:
            # Use original master data
            master_sheet = list(file_data['sheets'].keys())[0]  # Get first sheet
            file_data['sheets'][master_sheet].to_excel(temp_file, index=False)

        # Upload to SharePoint with backup
        upload_result = client.upload_processed_file(
            request.folder_path,
            request.file_name,
            temp_file,
            request.create_backup
        )

        # Cleanup
        os.remove(temp_file)
        os.rmdir(temp_dir)

        if upload_result["success"]:
            return SharePointUploadResponse(
                success=True,
                message="File uploaded to SharePoint successfully",
                uploaded_file=request.file_name,
                backup_created=upload_result.get("backup_created"),
                upload_timestamp=upload_result["upload_timestamp"]
            )
        else:
            raise Exception(upload_result.get("error", "Upload failed"))

    except Exception as e:
        logger.error(f"SharePoint upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sharepoint/rollback", response_model=SharePointRollbackResponse)
async def rollback_sharepoint_file(request: SharePointRollbackRequest):
    """Rollback SharePoint file to a previous backup version"""
    try:
        from .core.sharepoint_client import SharePointClient

        client = SharePointClient(request.site_url, request.username, request.password)

        if not client.authenticate():
            raise HTTPException(status_code=401, detail="SharePoint authentication failed")

        # Perform rollback
        success = client.rollback_file(
            request.folder_path,
            request.original_file,
            request.backup_file
        )

        if success:
            return SharePointRollbackResponse(
                success=True,
                message=f"Successfully rolled back {request.original_file} to {request.backup_file}",
                restored_file=request.original_file,
                rollback_timestamp=datetime.now().isoformat()
            )
        else:
            raise Exception("Rollback operation failed")

    except Exception as e:
        logger.error(f"SharePoint rollback failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sharepoint/history/{file_name}")
async def get_file_history(file_name: str, site_url: str, username: str, password: str, folder_path: str):
    """Get version history for a SharePoint file"""
    try:
        from .core.sharepoint_client import SharePointClient

        client = SharePointClient(site_url, username, password)

        if not client.authenticate():
            raise HTTPException(status_code=401, detail="SharePoint authentication failed")

        history = client.get_file_history(folder_path, file_name)

        return {
            "success": True,
            "message": f"Found {len(history)} versions for {file_name}",
            "file_history": history
        }

    except Exception as e:
        logger.error(f"File history retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-column")
async def analyze_column_distribution(request: Dict[str, Any]):
    """Analyze distribution of values in a specific column"""
    try:
        file_id = request["file_id"]
        sheet_name = request["sheet_name"]
        column_name = request["column_name"]

        # Get the sheet data
        df = file_manager.get_sheet(file_id, sheet_name)

        if column_name not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{column_name}' not found")

        # Analyze distribution
        value_counts = df[column_name].value_counts(dropna=False)

        # Categorize values
        distribution = {
            "X": int(value_counts.get("X", 0)),
            "D": int(value_counts.get("D", 0)),
            "0": int(value_counts.get("0", 0)) + int(value_counts.get(0, 0)),  # Handle both string and numeric 0
            "OTHER": 0
        }

        # Count other values
        for value, count in value_counts.items():
            if str(value) not in ["X", "D", "0"] and pd.notna(value):
                distribution["OTHER"] += int(count)

        # Add NaN/empty count to OTHER
        nan_count = df[column_name].isna().sum()
        distribution["OTHER"] += int(nan_count)

        # Create detailed breakdown
        detailed_breakdown = []
        for value, count in value_counts.items():
            category = "X" if value == "X" else "D" if value == "D" else "0" if str(value) == "0" else "OTHER"
            detailed_breakdown.append({
                "Value": str(value) if pd.notna(value) else "Empty/NaN",
                "Count": int(count),
                "Category": category,
                "Percentage": round((count / len(df)) * 100, 2)
            })

        # Add NaN count if exists
        if nan_count > 0:
            detailed_breakdown.append({
                "Value": "Empty/NaN",
                "Count": int(nan_count),
                "Category": "OTHER",
                "Percentage": round((nan_count / len(df)) * 100, 2)
            })

        # Sort by count descending
        detailed_breakdown.sort(key=lambda x: x["Count"], reverse=True)

        logger.info(f"Column analysis completed for {column_name}: {distribution}")

        return {
            "success": True,
            "message": f"Analysis completed for column '{column_name}'",
            "column_name": column_name,
            "total_rows": len(df),
            "distribution": distribution,
            "detailed_breakdown": detailed_breakdown
        }

    except Exception as e:
        logger.error(f"Column analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-column-filtered")
async def analyze_column_distribution_filtered(request: Dict[str, Any]):
    """Analyze distribution of values in a specific column for items NOT in target sheet"""
    try:
        file_id = request["file_id"]
        master_sheet = request["master_sheet"]
        target_sheet = request["target_sheet"]
        column_name = request["column_name"]

        # Get the sheet data
        master_df = file_manager.get_sheet(file_id, master_sheet)
        target_df = file_manager.get_sheet(file_id, target_sheet)

        if column_name not in master_df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{column_name}' not found in master sheet")

        if 'YAZAKI PN' not in master_df.columns:
            raise HTTPException(status_code=400, detail="'YAZAKI PN' column not found in master sheet")

        if 'YAZAKI PN' not in target_df.columns:
            raise HTTPException(status_code=400, detail="'YAZAKI PN' column not found in target sheet")

        # Get YAZAKI PNs from target sheet
        target_yazaki_pns = set(target_df['YAZAKI PN'].astype(str).str.strip())

        # Filter master data to only include items NOT in target sheet
        master_df_copy = master_df.copy()
        master_df_copy['YAZAKI PN'] = master_df_copy['YAZAKI PN'].astype(str).str.strip()

        # Filter for items NOT in target sheet
        not_in_target = ~master_df_copy['YAZAKI PN'].isin(target_yazaki_pns)
        filtered_df = master_df_copy[not_in_target]

        logger.info(f"Filtered analysis: {len(master_df_copy)} total items, {len(filtered_df)} not in target sheet")

        if len(filtered_df) == 0:
            return {
                "success": True,
                "message": f"No items found in Master BOM that are not in Target sheet",
                "column_name": column_name,
                "total_master_rows": len(master_df_copy),
                "filtered_rows": 0,
                "distribution": {"X": 0, "D": 0, "0": 0, "OTHER": 0},
                "detailed_breakdown": []
            }

        # Analyze distribution of the filtered data
        value_counts = filtered_df[column_name].value_counts(dropna=False)

        # Categorize values
        distribution = {
            "X": int(value_counts.get("X", 0)),
            "D": int(value_counts.get("D", 0)),
            "0": int(value_counts.get("0", 0)) + int(value_counts.get(0, 0)),  # Handle both string and numeric 0
            "OTHER": 0
        }

        # Count other values
        for value, count in value_counts.items():
            if str(value) not in ["X", "D", "0"] and pd.notna(value):
                distribution["OTHER"] += int(count)

        # Add NaN/empty count to OTHER
        nan_count = filtered_df[column_name].isna().sum()
        distribution["OTHER"] += int(nan_count)

        # Create detailed breakdown
        detailed_breakdown = []
        for value, count in value_counts.items():
            category = "X" if value == "X" else "D" if value == "D" else "0" if str(value) == "0" else "OTHER"
            detailed_breakdown.append({
                "Value": str(value) if pd.notna(value) else "Empty/NaN",
                "Count": int(count),
                "Category": category,
                "Percentage": round((count / len(filtered_df)) * 100, 2),
                "Status": "Not in Target Sheet"
            })

        # Add NaN count if exists
        if nan_count > 0:
            detailed_breakdown.append({
                "Value": "Empty/NaN",
                "Count": int(nan_count),
                "Category": "OTHER",
                "Percentage": round((nan_count / len(filtered_df)) * 100, 2),
                "Status": "Not in Target Sheet"
            })

        # Sort by count descending
        detailed_breakdown.sort(key=lambda x: x["Count"], reverse=True)

        logger.info(f"Filtered column analysis completed for {column_name}: {distribution}")

        return {
            "success": True,
            "message": f"Filtered analysis completed for column '{column_name}' (items not in target sheet)",
            "column_name": column_name,
            "total_master_rows": len(master_df_copy),
            "filtered_rows": len(filtered_df),
            "target_sheet": target_sheet,
            "distribution": distribution,
            "detailed_breakdown": detailed_breakdown
        }

    except Exception as e:
        logger.error(f"Filtered column analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-preexisting")
async def process_preexisting_items(request: Dict[str, Any]):
    """Process pre-existing items: Update X → D for items not in target sheet"""
    try:
        file_id = request["file_id"]
        master_sheet = request["master_sheet"]
        target_sheet = request["target_sheet"]
        column_name = request["column_name"]

        # Get the data
        master_df = file_manager.get_sheet(file_id, master_sheet)
        target_df = file_manager.get_sheet(file_id, target_sheet)

        if column_name not in master_df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{column_name}' not found in master sheet")

        if 'YAZAKI PN' not in master_df.columns:
            raise HTTPException(status_code=400, detail="'YAZAKI PN' column not found in master sheet")

        if 'YAZAKI PN' not in target_df.columns:
            raise HTTPException(status_code=400, detail="'YAZAKI PN' column not found in target sheet")

        # Get YAZAKI PNs from target sheet
        target_yazaki_pns = set(target_df['YAZAKI PN'].astype(str).str.strip())

        # Find items in master that are:
        # 1. Not in target sheet
        # 2. Have status 'X' in the specified column
        master_df_copy = master_df.copy()
        master_df_copy['YAZAKI PN'] = master_df_copy['YAZAKI PN'].astype(str).str.strip()

        # Create mask for items to update
        not_in_target = ~master_df_copy['YAZAKI PN'].isin(target_yazaki_pns)
        has_x_status = master_df_copy[column_name].astype(str).str.strip() == 'X'
        items_to_update = not_in_target & has_x_status

        # Debug logging
        logger.info(f"Target sheet has {len(target_yazaki_pns)} unique YAZAKI PNs")
        logger.info(f"Master BOM has {len(master_df_copy)} total records")
        logger.info(f"Items not in target: {not_in_target.sum()}")
        logger.info(f"Items with 'X' status: {has_x_status.sum()}")
        logger.info(f"Items to update (not in target AND has X): {items_to_update.sum()}")

        # Store original state for rollback
        original_master_df = master_df_copy.copy()

        # Calculate original distribution (entire Master BOM)
        original_value_counts = master_df_copy[column_name].value_counts(dropna=False)
        original_distribution = {
            "X": int(original_value_counts.get("X", 0)),
            "D": int(original_value_counts.get("D", 0)),
            "0": int(original_value_counts.get("0", 0)) + int(original_value_counts.get(0, 0)),
            "OTHER": 0
        }

        # Count other values in original
        for value, count in original_value_counts.items():
            if str(value) not in ["X", "D", "0"] and pd.notna(value):
                original_distribution["OTHER"] += int(count)

        # Add NaN/empty count to OTHER in original
        original_nan_count = master_df_copy[column_name].isna().sum()
        original_distribution["OTHER"] += int(original_nan_count)

        # Count items
        total_checked = len(master_df_copy)
        not_in_target_count = not_in_target.sum()
        updated_count = items_to_update.sum()

        logger.info(f"Pre-existing processing: {updated_count} items will be updated from X to D")
        logger.info(f"Original distribution - X: {original_distribution['X']}, D: {original_distribution['D']}")

        # Update the items
        master_df_copy.loc[items_to_update, column_name] = 'D'

        # Get preview of updated items
        updated_items = master_df_copy[items_to_update].copy()
        updated_items_preview = []

        if len(updated_items) > 0:
            # Show first 10 updated items
            preview_items = updated_items.head(10)
            for _, row in preview_items.iterrows():
                updated_items_preview.append({
                    "YAZAKI PN": row['YAZAKI PN'],
                    "Previous Status": "X",
                    "New Status": "D",
                    "Reason": "Not in target sheet",
                    f"{column_name}": row[column_name]
                })

        # Calculate new distribution
        new_value_counts = master_df_copy[column_name].value_counts(dropna=False)
        new_distribution = {
            "X": int(new_value_counts.get("X", 0)),
            "D": int(new_value_counts.get("D", 0)),
            "0": int(new_value_counts.get("0", 0)) + int(new_value_counts.get(0, 0)),
            "OTHER": 0
        }

        # Count other values
        for value, count in new_value_counts.items():
            if str(value) not in ["X", "D", "0"] and pd.notna(value):
                new_distribution["OTHER"] += int(count)

        # Add NaN/empty count to OTHER
        nan_count = master_df_copy[column_name].isna().sum()
        new_distribution["OTHER"] += int(nan_count)

        # Store original state for rollback before updating
        file_manager.files_storage[file_id]["original_master_backup"] = original_master_df.copy()
        file_manager.files_storage[file_id]["backup_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "column_name": column_name,
            "updated_count": int(updated_count),
            "original_distribution": original_distribution
        }

        # Update the file manager with the modified data
        file_manager.update_sheet(file_id, master_sheet, master_df_copy)

        logger.info(f"Pre-existing items processed: {updated_count} items updated from X to D")
        logger.info(f"New distribution - X: {new_distribution['X']}, D: {new_distribution['D']}")
        logger.info(f"Original state backed up for rollback capability")

        # Verify the math
        expected_new_x = original_distribution['X'] - updated_count
        expected_new_d = original_distribution['D'] + updated_count
        logger.info(f"Expected after update - X: {expected_new_x}, D: {expected_new_d}")

        return {
            "success": True,
            "message": f"Successfully updated {updated_count} items from 'X' to 'D'",
            "updated_count": int(updated_count),
            "total_checked": int(total_checked),
            "not_in_target_count": int(not_in_target_count),
            "column_name": column_name,
            "original_distribution": original_distribution,
            "new_distribution": new_distribution,
            "expected_new_x": int(expected_new_x),
            "expected_new_d": int(expected_new_d),
            "updated_items_preview": updated_items_preview,
            "rollback_available": True
        }

    except Exception as e:
        logger.error(f"Pre-existing items processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rollback-preexisting")
async def rollback_preexisting_changes(request: Dict[str, Any]):
    """Rollback pre-existing items changes to original state"""
    try:
        file_id = request["file_id"]
        master_sheet = request["master_sheet"]

        # Check if backup exists
        if file_id not in file_manager.files_storage:
            raise HTTPException(status_code=404, detail="File not found")

        file_data = file_manager.files_storage[file_id]

        if "original_master_backup" not in file_data:
            raise HTTPException(status_code=404, detail="No backup available for rollback")

        # Get backup data
        original_master_df = file_data["original_master_backup"]
        backup_metadata = file_data.get("backup_metadata", {})

        # Restore original state
        file_manager.update_sheet(file_id, master_sheet, original_master_df)

        # Calculate current distribution for comparison
        column_name = backup_metadata.get("column_name", "UNKNOWN")
        if column_name != "UNKNOWN" and column_name in original_master_df.columns:
            restored_value_counts = original_master_df[column_name].value_counts(dropna=False)
            restored_distribution = {
                "X": int(restored_value_counts.get("X", 0)),
                "D": int(restored_value_counts.get("D", 0)),
                "0": int(restored_value_counts.get("0", 0)) + int(restored_value_counts.get(0, 0)),
                "OTHER": 0
            }

            # Count other values
            for value, count in restored_value_counts.items():
                if str(value) not in ["X", "D", "0"] and pd.notna(value):
                    restored_distribution["OTHER"] += int(count)

            # Add NaN/empty count to OTHER
            nan_count = original_master_df[column_name].isna().sum()
            restored_distribution["OTHER"] += int(nan_count)
        else:
            restored_distribution = {}

        # Clear backup after successful rollback
        del file_data["original_master_backup"]
        if "backup_metadata" in file_data:
            del file_data["backup_metadata"]

        logger.info(f"Rollback completed for file {file_id}, restored {len(original_master_df)} records")

        return {
            "success": True,
            "message": "Successfully rolled back to original state",
            "restored_records": len(original_master_df),
            "backup_timestamp": backup_metadata.get("timestamp", "Unknown"),
            "restored_distribution": restored_distribution,
            "column_name": column_name,
            "rollback_available": False
        }

    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rollback-status/{file_id}")
async def get_rollback_status(file_id: str):
    """Check if rollback is available for a file"""
    try:
        if file_id not in file_manager.files_storage:
            raise HTTPException(status_code=404, detail="File not found")

        file_data = file_manager.files_storage[file_id]
        backup_available = "original_master_backup" in file_data
        backup_metadata = file_data.get("backup_metadata", {})

        return {
            "success": True,
            "rollback_available": backup_available,
            "backup_metadata": backup_metadata
        }

    except Exception as e:
        logger.error(f"Rollback status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs/export/{format}")
async def export_logs(format: str):
    """Export logs in different formats (text, json, csv)"""
    try:
        from fastapi.responses import PlainTextResponse

        if format.lower() == "text":
            content = log_manager.export_logs_as_text()
            return PlainTextResponse(
                content=content,
                headers={"Content-Disposition": f"attachment; filename=etl_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"}
            )
        elif format.lower() == "json":
            content = log_manager.export_logs_as_json()
            return PlainTextResponse(
                content=content,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=etl_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
            )
        elif format.lower() == "csv":
            content = log_manager.export_logs_as_csv()
            return PlainTextResponse(
                content=content,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=etl_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'text', 'json', or 'csv'")

    except Exception as e:
        logger.error(f"Log export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs/summary")
async def get_log_summary():
    """Get summary of current logs"""
    try:
        return log_manager.get_log_summary()
    except Exception as e:
        logger.error(f"Log summary failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/logs/clear")
async def clear_logs():
    """Clear all logs"""
    try:
        log_manager.clear_logs()
        return {"success": True, "message": "All logs cleared"}
    except Exception as e:
        logger.error(f"Log clearing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear-cache")
async def clear_cache():
    """Clear all cached files for performance optimization"""
    try:
        file_manager.clear_all_cache()
        logger.info("Cache cleared successfully via API")
        return {
            "success": True,
            "message": "All cached files cleared for performance optimization"
        }
    except Exception as e:
        logger.error(f"Cache clearing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/dashboard/data")
async def get_dashboard_data():
    """Generate dashboard data from uploaded file"""
    try:
        session_data = get_session_data()

        if not session_data.get("file_id"):
            raise HTTPException(status_code=400, detail="No file uploaded")

        file_path = session_data.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Read the Excel file
        excel_data = pd.ExcelFile(file_path)

        # Initialize dashboard data
        dashboard_data = {
            "kpis": {},
            "status_breakdown": [],
            "bom_analysis": {},
            "time_series_data": [],
            "top_products": []
        }

        # Process MasterBOM sheet if available
        if "MasterBOM" in excel_data.sheet_names:
            master_bom = pd.read_excel(file_path, sheet_name="MasterBOM")

            # Generate BOM analysis
            dashboard_data["bom_analysis"] = {
                "total_parts": len(master_bom),
                "active_parts": len(master_bom[master_bom.get("Status", "") == "D"]),
                "inactive_parts": len(master_bom[master_bom.get("Status", "") == "X"]),
                "pending_parts": len(master_bom[master_bom.get("Status", "") == "0"]),
                "category_breakdown": []
            }

            # Category breakdown
            if "Category" in master_bom.columns:
                category_counts = master_bom["Category"].value_counts()
                total_parts = len(master_bom)
                dashboard_data["bom_analysis"]["category_breakdown"] = [
                    {
                        "category": cat,
                        "count": int(count),
                        "percentage": round((count / total_parts) * 100, 1)
                    }
                    for cat, count in category_counts.head(10).items()
                ]

        # Process Status sheet if available
        if "Status" in excel_data.sheet_names:
            status_data = pd.read_excel(file_path, sheet_name="Status")

            # Status breakdown
            if "Status" in status_data.columns:
                status_counts = status_data["Status"].value_counts()
                total_status = len(status_data)

                status_mapping = {
                    "D": {"name": "Active (D)", "color": "#52c41a"},
                    "0": {"name": "Check (0)", "color": "#faad14"},
                    "X": {"name": "Inactive (X)", "color": "#ff4d4f"},
                    "NOT_FOUND": {"name": "Not Found", "color": "#13c2c2"}
                }

                dashboard_data["status_breakdown"] = [
                    {
                        "name": status_mapping.get(status, {"name": str(status), "color": "#1890ff"})["name"],
                        "value": int(count),
                        "color": status_mapping.get(status, {"name": str(status), "color": "#1890ff"})["color"],
                        "percentage": round((count / total_status) * 100, 1)
                    }
                    for status, count in status_counts.items()
                ]

        # Generate KPIs
        dashboard_data["kpis"] = {
            "total_customers": 567899,
            "total_revenue": 3465000,
            "total_orders": 1136,
            "total_returns": 1789,
            "customer_growth": 2.5,
            "revenue_growth": 5.8,
            "order_growth": -0.2,
            "return_growth": 0.12
        }

        # Generate time series data (mock)
        import datetime
        now = datetime.datetime.now()
        dashboard_data["time_series_data"] = [
            {
                "date": (now - datetime.timedelta(days=i)).strftime("%Y-%m-%d"),
                "orders": 50 + (i * 2),
                "revenue": 25000 + (i * 1000),
                "customers": 100 + (i * 3)
            }
            for i in range(30, 0, -1)
        ]

        # Generate top products (mock)
        dashboard_data["top_products"] = [
            {
                "part_number": f"YZK-{str(i).zfill(4)}",
                "description": f"Component {i}",
                "quantity": 100 + (i * 10),
                "revenue": 10000 + (i * 1000),
                "status": ["Active", "Pending", "Inactive"][i % 3]
            }
            for i in range(1, 11)
        ]

        return dashboard_data

    except Exception as e:
        logger.error(f"Dashboard data generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bom/analysis")
async def get_bom_analysis():
    """Generate detailed BOM analysis"""
    try:
        session_data = get_session_data()

        if not session_data.get("file_id"):
            raise HTTPException(status_code=400, detail="No file uploaded")

        file_path = session_data.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Read the Excel file
        excel_data = pd.ExcelFile(file_path)

        bom_data = []
        category_analysis = []

        # Process MasterBOM sheet if available
        if "MasterBOM" in excel_data.sheet_names:
            master_bom = pd.read_excel(file_path, sheet_name="MasterBOM")

            # Convert to list of dictionaries for frontend
            for _, row in master_bom.iterrows():
                bom_data.append({
                    "part_number": str(row.get("Part Number", "")),
                    "description": str(row.get("Description", "")),
                    "category": str(row.get("Category", "Unknown")),
                    "status": str(row.get("Status", "NOT_FOUND")),
                    "quantity": int(row.get("Quantity", 0)),
                    "unit_cost": float(row.get("Unit Cost", 0)),
                    "total_cost": float(row.get("Total Cost", 0)),
                    "supplier": str(row.get("Supplier", "Unknown")),
                    "last_updated": str(row.get("Last Updated", "")),
                    "criticality": str(row.get("Criticality", "Medium"))
                })

            # Generate category analysis
            if "Category" in master_bom.columns:
                categories = master_bom.groupby("Category").agg({
                    "Part Number": "count",
                    "Status": lambda x: (x == "D").sum(),
                    "Total Cost": "sum"
                }).reset_index()

                for _, cat_row in categories.iterrows():
                    category_analysis.append({
                        "category": cat_row["Category"],
                        "total_parts": int(cat_row["Part Number"]),
                        "active_parts": int(cat_row["Status"]),
                        "total_value": float(cat_row["Total Cost"]),
                        "average_cost": float(cat_row["Total Cost"] / cat_row["Part Number"]) if cat_row["Part Number"] > 0 else 0
                    })

        return {
            "bom_data": bom_data,
            "category_analysis": category_analysis
        }

    except Exception as e:
        logger.error(f"BOM analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SESSION-BASED ENDPOINTS FOR REACT FRONTEND COMPATIBILITY
# ============================================================================

@app.post("/preview-session")
async def preview_sheets_session(request: dict):
    """Session-based preview endpoint for React frontend"""
    try:
        logger.info(f"Preview session request: {request}")

        master_sheet = request.get("master_sheet")
        target_sheet = request.get("target_sheet")

        logger.info(f"Requested sheets - Master: {master_sheet}, Target: {target_sheet}")

        if not master_sheet or not target_sheet:
            raise HTTPException(status_code=400, detail="master_sheet and target_sheet are required")

        # Find the most recent file_id from session storage
        if not session_storage:
            # Try to rebuild session storage from file_manager
            rebuild_session_storage()

        if not session_storage:
            raise HTTPException(status_code=400, detail="No file uploaded. Please upload a file first.")

        logger.info(f"Session storage keys: {list(session_storage.keys())}")

        # Get the most recent file_id
        file_id = list(session_storage.keys())[-1]
        session_data = session_storage[file_id]

        logger.info(f"Using file_id: {file_id}")
        available_sheets = session_data.get('sheet_names', [])
        logger.info(f"Available sheets: {available_sheets}")

        # Validate that requested sheets exist
        if master_sheet not in available_sheets:
            raise HTTPException(
                status_code=400,
                detail=f"Master sheet '{master_sheet}' not found. Available sheets: {available_sheets}"
            )

        if target_sheet not in available_sheets:
            raise HTTPException(
                status_code=400,
                detail=f"Target sheet '{target_sheet}' not found. Available sheets: {available_sheets}"
            )

        # Update session with selected sheets
        session_data['master_sheet'] = master_sheet
        session_data['target_sheet'] = target_sheet

        # Get previews
        previews = file_manager.preview_sheets(file_id, [master_sheet, target_sheet])

        logger.info(f"Preview generated successfully for {len(previews)} sheets")

        return {
            "success": True,
            "previews": previews
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session preview failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clean-session")
async def clean_data_session():
    """Session-based cleaning endpoint for React frontend"""
    try:
        if not session_storage:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Get the most recent session
        file_id = list(session_storage.keys())[-1]
        session_data = session_storage[file_id]

        if not session_data.get('master_sheet') or not session_data.get('target_sheet'):
            raise HTTPException(status_code=400, detail="Please preview sheets first")

        # Get original sheets
        master_df = file_manager.get_sheet(file_id, session_data['master_sheet'])
        target_df = file_manager.get_sheet(file_id, session_data['target_sheet'])

        # Clean master sheet (YAZAKI PN only)
        master_cleaned, master_stats = data_cleaner.clean_master_yazaki(master_df)

        # Clean target sheet
        target_cleaned, target_stats = data_cleaner.clean_generic_sheet(target_df)
        target_cleaned = data_cleaner.prepare_target_sheet(target_cleaned)

        # Store cleaned data
        file_manager.update_sheet(file_id, session_data['master_sheet'], master_cleaned)
        file_manager.update_sheet(file_id, session_data['target_sheet'], target_cleaned)

        return {
            "success": True,
            "message": "Data cleaning completed successfully",
            "master_preview": master_cleaned[["YAZAKI PN"]].head(5).fillna('').to_dict('records'),
            "target_preview": target_cleaned.head(5).fillna('').to_dict('records'),
            "master_shape": list(master_cleaned.shape),
            "target_shape": list(target_cleaned.shape)
        }

    except Exception as e:
        logger.error(f"Session cleaning failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-lookup-columns")
async def get_lookup_columns_session():
    """Session-based get lookup columns endpoint for React frontend"""
    try:
        if not session_storage:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Get the most recent session
        file_id = list(session_storage.keys())[-1]
        session_data = session_storage[file_id]

        if not session_data.get('master_sheet'):
            raise HTTPException(status_code=400, detail="Please clean data first")

        master_df = file_manager.get_processed_sheet(file_id, session_data['master_sheet'])
        columns = data_processor.get_column_suggestions(master_df)

        return {"success": True, "columns": columns}

    except Exception as e:
        logger.error(f"Session get columns failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lookup-session")
async def perform_lookup_session(request: dict):
    """Session-based lookup endpoint for React frontend"""
    try:
        lookup_column = request.get("lookup_column")
        if not lookup_column:
            raise HTTPException(status_code=400, detail="lookup_column is required")

        if not session_storage:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Get the most recent session
        file_id = list(session_storage.keys())[-1]
        session_data = session_storage[file_id]

        if not session_data.get('master_sheet') or not session_data.get('target_sheet'):
            raise HTTPException(status_code=400, detail="Please clean data first")

        # Get cleaned sheets
        master_df = file_manager.get_processed_sheet(file_id, session_data['master_sheet'])
        target_df = file_manager.get_processed_sheet(file_id, session_data['target_sheet'])

        # Perform lookup
        result_df, stats = data_processor.add_activation_status(
            master_df, target_df, "YAZAKI PN", lookup_column
        )

        # Store result
        file_manager.update_sheet(file_id, session_data['target_sheet'], result_df)

        return {
            "success": True,
            "message": "Lookup completed successfully",
            "result_preview": result_df.head(20).fillna('').to_dict('records'),
            "total_records": stats["total_processed"],
            "successful_matches": stats["mapping_results"].get("Found", 0),
            "failed_matches": stats["mapping_results"].get("Not Found", 0),
            "lookup_column": lookup_column
        }

    except Exception as e:
        logger.error(f"Session lookup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/column-insights")
async def generate_column_insights():
    """Generate insights about cleaned data columns"""
    try:
        if not session_storage:
            rebuild_session_storage()

        if not session_storage:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Get the most recent session
        file_id = list(session_storage.keys())[-1]
        session_data = session_storage[file_id]

        if not session_data.get('master_sheet') or not session_data.get('target_sheet'):
            raise HTTPException(status_code=400, detail="Please clean data first")

        # Get cleaned sheets
        master_df = file_manager.get_processed_sheet(file_id, session_data['master_sheet'])
        target_df = file_manager.get_processed_sheet(file_id, session_data['target_sheet'])

        # Generate column insights (convert numpy types to Python types for JSON serialization)
        insights = {
            "master_sheet_analysis": {
                "total_columns": int(len(master_df.columns)),
                "total_rows": int(len(master_df)),
                "yazaki_pn_column": "YAZAKI PN" in master_df.columns,
                "yazaki_pn_unique_count": int(master_df["YAZAKI PN"].nunique()) if "YAZAKI PN" in master_df.columns else 0,
                "yazaki_pn_null_count": int(master_df["YAZAKI PN"].isnull().sum()) if "YAZAKI PN" in master_df.columns else 0,
                "column_types": {col: str(dtype) for col, dtype in master_df.dtypes.items()},
                "sample_data": master_df.head(3).fillna('').to_dict('records')
            },
            "target_sheet_analysis": {
                "total_columns": int(len(target_df.columns)),
                "total_rows": int(len(target_df)),
                "column_types": {col: str(dtype) for col, dtype in target_df.dtypes.items()},
                "sample_data": target_df.head(3).fillna('').to_dict('records')
            },
            "data_quality": {
                "master_completeness": {col: float(val) for col, val in ((master_df.notna().sum() / len(master_df)) * 100).round(2).items()},
                "target_completeness": {col: float(val) for col, val in ((target_df.notna().sum() / len(target_df)) * 100).round(2).items()},
            }
        }

        logger.info(f"Column insights generated for {len(master_df)} master records and {len(target_df)} target records")

        return {
            "success": True,
            "message": "Column insights generated successfully",
            "insights": insights
        }

    except Exception as e:
        logger.error(f"Column insights failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/lookup-insights")
async def generate_lookup_insights():
    """Generate insights about lookup results"""
    try:
        if not session_storage:
            rebuild_session_storage()

        if not session_storage:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Get the most recent session
        file_id = list(session_storage.keys())[-1]
        session_data = session_storage[file_id]

        if not session_data.get('target_sheet'):
            raise HTTPException(status_code=400, detail="Please perform lookup first")

        # Get lookup results
        target_df = file_manager.get_processed_sheet(file_id, session_data['target_sheet'])

        # Check for activation status column (could be different names)
        activation_columns = [col for col in target_df.columns if 'activation' in col.lower() or 'status' in col.lower()]
        if not activation_columns:
            logger.warning(f"Available columns: {list(target_df.columns)}")
            raise HTTPException(status_code=400, detail="No lookup results found. Please perform lookup first.")

        activation_col = activation_columns[0]  # Use the first matching column

        # Generate lookup insights
        activation_counts = target_df[activation_col].value_counts().to_dict()
        total_records = int(len(target_df))

        # Convert numpy types to Python types for JSON serialization
        activation_counts_clean = {str(k): int(v) for k, v in activation_counts.items()}

        # Map status categories to match Streamlit format
        status_0 = activation_counts_clean.get('0', 0)
        status_d = activation_counts_clean.get('D', 0)
        status_x = activation_counts_clean.get('X', 0)
        not_found = activation_counts_clean.get('', 0) + activation_counts_clean.get('NOT_FOUND', 0)

        # Calculate match rate (found vs not found)
        found_records = status_0 + status_d + status_x
        match_rate = round((found_records / total_records) * 100, 2) if total_records > 0 else 0

        insights = {
            "lookup_summary": {
                "total_records": total_records,
                "activation_status_distribution": {
                    "0": status_0,
                    "D": status_d,
                    "X": status_x,
                    "NOT_FOUND": not_found
                },
                "activation_percentages": {
                    "0": round((status_0 / total_records) * 100, 2) if total_records > 0 else 0,
                    "D": round((status_d / total_records) * 100, 2) if total_records > 0 else 0,
                    "X": round((status_x / total_records) * 100, 2) if total_records > 0 else 0,
                    "NOT_FOUND": round((not_found / total_records) * 100, 2) if total_records > 0 else 0
                },
                "successful_matches": found_records,
                "failed_matches": not_found
            },
            "data_quality_insights": {
                "match_rate": match_rate,
                "status_0_parts": status_0,  # Status '0' (inactive/check)
                "status_d_parts": status_d,  # Status 'D' (active/discontinued)
                "status_x_parts": status_x,  # Status 'X' (inactive/no update)
                "not_found_parts": not_found  # Not found in master
            },
            "kpi_counts": {
                "0": status_0,
                "D": status_d,
                "X": status_x,
                "NOT_FOUND": not_found
            },
            "recommendations": []
        }

        # Add recommendations based on results (matching Streamlit format)
        match_rate = insights["data_quality_insights"]["match_rate"]
        if match_rate < 80:
            insights["recommendations"].append("Low match rate detected. Consider reviewing YAZAKI PN formatting.")
        if not_found > total_records * 0.1:
            insights["recommendations"].append("High number of parts not found in master data. Review master data completeness.")
        if status_x > status_d:
            insights["recommendations"].append("More inactive (X) than active (D) parts detected. Review part lifecycle status.")
        if status_0 > (status_d + status_x):
            insights["recommendations"].append("High number of status '0' parts. Consider reviewing activation criteria.")

        # Add status-specific insights
        if status_d > 0:
            insights["recommendations"].append(f"Found {status_d} active parts (Status 'D') ready for processing.")
        if status_x > 0:
            insights["recommendations"].append(f"Found {status_x} inactive parts (Status 'X') that may need review.")
        if status_0 > 0:
            insights["recommendations"].append(f"Found {status_0} parts with status '0' requiring activation check.")

        logger.info(f"Lookup insights generated: {match_rate}% match rate, {len(activation_counts)} status types")

        return {
            "success": True,
            "message": "Lookup insights generated successfully",
            "insights": insights
        }

    except Exception as e:
        logger.error(f"Lookup insights failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
