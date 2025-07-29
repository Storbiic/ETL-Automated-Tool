"""
Pydantic models for data validation and API schemas
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import pandas as pd


class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    success: bool
    message: str
    sheet_names: List[str]
    file_id: str


class SheetPreviewRequest(BaseModel):
    """Request model for sheet preview"""
    file_id: str
    sheet_names: List[str]


class SheetPreviewResponse(BaseModel):
    """Response model for sheet preview"""
    success: bool
    previews: Dict[str, List[Dict[str, Any]]]


class CleaningRequest(BaseModel):
    """Request model for data cleaning"""
    file_id: str
    master_sheet: str
    target_sheet: str


class CleaningResponse(BaseModel):
    """Response model for data cleaning"""
    success: bool
    message: str
    master_preview: List[Dict[str, Any]]
    target_preview: List[Dict[str, Any]]
    master_shape: List[int]
    target_shape: List[int]


class LookupRequest(BaseModel):
    """Request model for lookup operation"""
    file_id: str
    master_sheet: str
    target_sheet: str
    lookup_column: str
    key_column: str = "YAZAKI PN"


class LookupResponse(BaseModel):
    """Response model for lookup operation"""
    success: bool
    message: str
    result_preview: List[Dict[str, Any]]
    kpi_counts: Dict[str, int]
    total_records: int
    download_url: str


class ColumnSuggestionRequest(BaseModel):
    """Request model for column suggestion"""
    input_name: str
    available_columns: List[str]


class ColumnSuggestionResponse(BaseModel):
    """Response model for column suggestion"""
    suggested_column: str
    confidence: float


class MasterUpdateRequest(BaseModel):
    """Request model for Master BOM updates"""
    file_id: str
    master_sheet: str
    target_sheet: str
    lookup_column: str


class MasterUpdateResponse(BaseModel):
    """Response model for Master BOM updates"""
    success: bool
    message: str
    updated_count: int
    inserted_count: int
    duplicates_count: int
    skipped_count: int
    duplicates: List[Dict[str, Any]]


class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error: str
    details: Optional[str] = None
