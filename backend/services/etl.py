import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import io
from datetime import datetime
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
import logging

from backend.models.schema import (
    FilterRequest, JoinRequest, UploadResponse, DataResponse, 
    FilterResponse, JoinResponse, FileMetadata, SheetMetadata, 
    FilterConfig, CommonKey
)
from shared.utils import detect_file_type, clean_dataframe, generate_column_filters

logger = logging.getLogger(__name__)

class ETLService:
    def __init__(self):
        # In-memory storage for processed data
        self.data_store: Dict[str, Dict[str, pd.DataFrame]] = {}
        self.metadata_store: Dict[str, FileMetadata] = {}
    
    async def process_uploaded_file(self, file: UploadFile, file_id: str) -> UploadResponse:
        """Process uploaded file and return metadata"""
        try:
            file_type = detect_file_type(file.filename)
            content = await file.read()
            
            sheets = {}
            
            if file_type == 'csv':
                # Read CSV file
                df = pd.read_csv(io.BytesIO(content))
                sheets['Sheet1'] = clean_dataframe(df)
            else:
                # Read Excel file
                excel_file = pd.ExcelFile(io.BytesIO(content))
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    sheets[sheet_name] = clean_dataframe(df)
            
            # Store data
            self.data_store[file_id] = sheets
            
            # Generate metadata
            sheet_metadata = {}
            for sheet_name, df in sheets.items():
                filters = generate_column_filters(df)
                filter_configs = {}
                for col, filter_data in filters.items():
                    filter_configs[col] = FilterConfig(**filter_data)
                
                sheet_metadata[sheet_name] = SheetMetadata(
                    rows=len(df),
                    columns=len(df.columns),
                    column_names=list(df.columns),
                    column_types={col: str(df[col].dtype) for col in df.columns},
                    filters=filter_configs
                )
            
            # Find common keys
            common_keys = []
            if len(sheets) > 1:
                common_keys_data = self._find_common_keys(sheets)
                common_keys = [CommonKey(**key_data) for key_data in common_keys_data]
            
            metadata = FileMetadata(
                filename=file.filename,
                file_type=file_type,
                upload_time=datetime.now().isoformat(),
                sheets=sheet_metadata,
                common_keys=common_keys
            )
            
            self.metadata_store[file_id] = metadata
            
            return UploadResponse(file_id=file_id, metadata=metadata)
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")
    
    def get_sheet_data(self, file_id: str, sheet_name: str, limit: int = 100) -> DataResponse:
        """Get data from a specific sheet"""
        if file_id not in self.data_store:
            raise HTTPException(status_code=404, detail="File not found")
        
        if sheet_name not in self.data_store[file_id]:
            raise HTTPException(status_code=404, detail="Sheet not found")
        
        df = self.data_store[file_id][sheet_name]
        result_df = df.head(limit).copy()
        
        # Handle datetime columns for JSON serialization
        for col in result_df.columns:
            if 'datetime' in str(result_df[col].dtype):
                result_df[col] = result_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return DataResponse(
            data=result_df.to_dict('records'),
            total_rows=len(df),
            columns=list(df.columns)
        )
    
    def apply_filters(self, request: FilterRequest) -> FilterResponse:
        """Apply filters to data"""
        if request.file_id not in self.data_store:
            raise HTTPException(status_code=404, detail="File not found")
        
        if request.sheet_name not in self.data_store[request.file_id]:
            raise HTTPException(status_code=404, detail="Sheet not found")
        
        df = self.data_store[request.file_id][request.sheet_name].copy()
        original_rows = len(df)
        
        # Apply filters
        for col, filter_config in request.filters.items():
            if col not in df.columns:
                continue
            
            if filter_config.type == 'categorical':
                if filter_config.selected:
                    df = df[df[col].isin(filter_config.selected)]
            
            elif filter_config.type == 'numeric':
                if filter_config.min is not None:
                    df = df[df[col] >= filter_config.min]
                if filter_config.max is not None:
                    df = df[df[col] <= filter_config.max]
            
            elif filter_config.type == 'date':
                if filter_config.min:
                    min_date = pd.to_datetime(filter_config.min)
                    df = df[df[col] >= min_date]
                if filter_config.max:
                    max_date = pd.to_datetime(filter_config.max)
                    df = df[df[col] <= max_date]
        
        # Handle datetime columns for JSON serialization
        display_df = df.copy()
        for col in display_df.columns:
            if 'datetime' in str(display_df[col].dtype):
                display_df[col] = display_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return FilterResponse(
            data=display_df.to_dict('records'),
            total_rows=original_rows,
            filtered_rows=len(df)
        )
    
    def join_sheets(self, request: JoinRequest) -> JoinResponse:
        """Join two sheets on specified keys"""
        if request.file_id not in self.data_store:
            raise HTTPException(status_code=404, detail="File not found")
        
        sheets = self.data_store[request.file_id]
        
        if request.left_sheet not in sheets or request.right_sheet not in sheets:
            raise HTTPException(status_code=404, detail="One or both sheets not found")
        
        left_df = sheets[request.left_sheet].copy()
        right_df = sheets[request.right_sheet].copy()
        
        # Perform join
        try:
            if request.join_type == "inner":
                result_df = pd.merge(left_df, right_df, left_on=request.left_key, right_on=request.right_key, how='inner', suffixes=('_left', '_right'))
            elif request.join_type == "left":
                result_df = pd.merge(left_df, right_df, left_on=request.left_key, right_on=request.right_key, how='left', suffixes=('_left', '_right'))
            elif request.join_type == "right":
                result_df = pd.merge(left_df, right_df, left_on=request.left_key, right_on=request.right_key, how='right', suffixes=('_left', '_right'))
            elif request.join_type == "outer":
                result_df = pd.merge(left_df, right_df, left_on=request.left_key, right_on=request.right_key, how='outer', suffixes=('_left', '_right'))
            else:
                raise HTTPException(status_code=400, detail="Invalid join type")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Join failed: {str(e)}")
        
        # Store joined result
        join_sheet_name = f"Joined_{request.left_sheet}_{request.right_sheet}"
        self.data_store[request.file_id][join_sheet_name] = result_df
        
        # Update metadata to include the joined sheet
        if hasattr(self, 'metadata_store') and request.file_id in self.metadata_store:
            filters = generate_column_filters(result_df)
            filter_configs = {}
            for col, filter_data in filters.items():
                filter_configs[col] = FilterConfig(**filter_data)
            
            new_sheet_metadata = SheetMetadata(
                rows=len(result_df),
                columns=len(result_df.columns),
                column_names=list(result_df.columns),
                column_types={col: str(result_df[col].dtype) for col in result_df.columns},
                filters=filter_configs
            )
            
            self.metadata_store[request.file_id].sheets[join_sheet_name] = new_sheet_metadata
        
        # Handle datetime columns for JSON serialization
        display_df = result_df.head(100).copy()
        for col in display_df.columns:
            if 'datetime' in str(display_df[col].dtype):
                display_df[col] = display_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return JoinResponse(
            joined_sheet_name=join_sheet_name,
            data=display_df.to_dict('records'),
            total_rows=len(result_df),
            columns=list(result_df.columns)
        )
    
    def download_csv(self, file_id: str, sheet_name: str) -> StreamingResponse:
        """Download processed data as CSV"""
        if file_id not in self.data_store:
            raise HTTPException(status_code=404, detail="File not found")
        
        if sheet_name not in self.data_store[file_id]:
            raise HTTPException(status_code=404, detail="Sheet not found")
        
        df = self.data_store[file_id][sheet_name]
        
        # Create CSV content
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        # Create streaming response
        response = StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{sheet_name}_processed.csv"'
            }
        )
        
        return response
    
    def get_metadata(self, file_id: str) -> FileMetadata:
        """Get file metadata"""
        if file_id not in self.metadata_store:
            raise HTTPException(status_code=404, detail="File not found")
        
        return self.metadata_store[file_id]
    
    def delete_data(self, file_id: str):
        """Delete stored data"""
        if file_id in self.data_store:
            del self.data_store[file_id]
        if file_id in self.metadata_store:
            del self.metadata_store[file_id]
    
    def _find_common_keys(self, sheets: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Find potential common keys across sheets"""
        common_keys = []
        sheet_names = list(sheets.keys())
        
        for i, sheet1_name in enumerate(sheet_names):
            for sheet2_name in sheet_names[i+1:]:
                sheet1_cols = set(sheets[sheet1_name].columns)
                sheet2_cols = set(sheets[sheet2_name].columns)
                common_cols = sheet1_cols.intersection(sheet2_cols)
                
                for col in common_cols:
                    # Check if the column has reasonable overlap in values
                    vals1 = set(sheets[sheet1_name][col].dropna().astype(str))
                    vals2 = set(sheets[sheet2_name][col].dropna().astype(str))
                    overlap = len(vals1.intersection(vals2))
                    
                    if overlap > 0:
                        common_keys.append({
                            'sheet1': sheet1_name,
                            'sheet2': sheet2_name,
                            'column': col,
                            'overlap_count': overlap
                        })
        
        # Sort by overlap count (descending)
        common_keys.sort(key=lambda x: x['overlap_count'], reverse=True)
        return common_keys