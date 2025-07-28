from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

class FilterConfig(BaseModel):
    type: str  # 'categorical', 'numeric', 'date'
    options: Optional[List[str]] = None
    min: Optional[Union[float, str]] = None
    max: Optional[Union[float, str]] = None
    selected: Optional[List[str]] = None

class FilterRequest(BaseModel):
    file_id: str
    sheet_name: str
    filters: Dict[str, FilterConfig]

class JoinRequest(BaseModel):
    file_id: str
    left_sheet: str
    right_sheet: str
    left_key: str
    right_key: str
    join_type: str = "inner"

class SheetMetadata(BaseModel):
    rows: int
    columns: int
    column_names: List[str]
    column_types: Dict[str, str]
    filters: Dict[str, FilterConfig]

class CommonKey(BaseModel):
    sheet1: str
    sheet2: str
    column: str
    overlap_count: int

class FileMetadata(BaseModel):
    filename: str
    file_type: str
    upload_time: str
    sheets: Dict[str, SheetMetadata]
    common_keys: List[CommonKey]

class UploadResponse(BaseModel):
    file_id: str
    metadata: FileMetadata

class DataResponse(BaseModel):
    data: List[Dict[str, Any]]
    total_rows: int
    columns: List[str]

class FilterResponse(BaseModel):
    data: List[Dict[str, Any]]
    total_rows: int
    filtered_rows: int

class JoinResponse(BaseModel):
    joined_sheet_name: str
    data: List[Dict[str, Any]]
    total_rows: int
    columns: List[str]

class HealthResponse(BaseModel):
    status: str
    timestamp: str