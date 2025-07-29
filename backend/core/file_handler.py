"""
Enhanced file handling with better error handling and validation
"""
import pandas as pd
import io
from typing import Dict, List, Union
import uuid
import os
from pathlib import Path


class FileManager:
    """Manages uploaded files and their processing"""
    
    def __init__(self):
        self.files_storage = {}  # In-memory storage for demo
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return file ID"""
        file_id = str(uuid.uuid4())
        
        # Save file to disk for persistence
        file_path = self.upload_dir / f"{file_id}_{filename}"
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Load and store sheets in memory for quick access
        try:
            sheets = self._load_file_from_bytes(file_content, filename)
            self.files_storage[file_id] = {
                "filename": filename,
                "file_path": str(file_path),
                "sheets": sheets,
                "processed_sheets": {}
            }
            return file_id
        except Exception as e:
            # Clean up file if loading failed
            if file_path.exists():
                file_path.unlink()
            raise e
    
    def _load_file_from_bytes(self, file_content: bytes, filename: str) -> Dict[str, pd.DataFrame]:
        """Load file from bytes and return sheets dictionary"""
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_content))
            return {"Sheet1": df}
        
        # For Excel files
        xl = pd.ExcelFile(io.BytesIO(file_content))
        return {name: xl.parse(name) for name in xl.sheet_names}
    
    def get_sheet_names(self, file_id: str) -> List[str]:
        """Get sheet names for a file"""
        if file_id not in self.files_storage:
            raise ValueError(f"File ID {file_id} not found")
        return list(self.files_storage[file_id]["sheets"].keys())
    
    def get_sheet(self, file_id: str, sheet_name: str) -> pd.DataFrame:
        """Get a specific sheet"""
        if file_id not in self.files_storage:
            raise ValueError(f"File ID {file_id} not found")
        
        sheets = self.files_storage[file_id]["sheets"]
        if sheet_name not in sheets:
            raise ValueError(f"Sheet {sheet_name} not found")
        
        return sheets[sheet_name].copy()
    
    def update_sheet(self, file_id: str, sheet_name: str, dataframe: pd.DataFrame):
        """Update a sheet with processed data"""
        if file_id not in self.files_storage:
            raise ValueError(f"File ID {file_id} not found")
        
        self.files_storage[file_id]["processed_sheets"][sheet_name] = dataframe.copy()
    
    def get_processed_sheet(self, file_id: str, sheet_name: str) -> pd.DataFrame:
        """Get processed sheet if available, otherwise return original"""
        if file_id not in self.files_storage:
            raise ValueError(f"File ID {file_id} not found")
        
        processed = self.files_storage[file_id]["processed_sheets"]
        if sheet_name in processed:
            return processed[sheet_name].copy()
        
        return self.get_sheet(file_id, sheet_name)
    
    def preview_sheets(self, file_id: str, sheet_names: List[str], rows: int = 5) -> Dict[str, List[Dict]]:
        """Get preview of multiple sheets"""
        previews = {}
        for sheet_name in sheet_names:
            df = self.get_sheet(file_id, sheet_name)
            previews[sheet_name] = df.head(rows).to_dict('records')
        return previews
    
    def cleanup_file(self, file_id: str):
        """Remove file from storage and disk"""
        if file_id in self.files_storage:
            file_path = Path(self.files_storage[file_id]["file_path"])
            if file_path.exists():
                file_path.unlink()
            del self.files_storage[file_id]


# Global file manager instance
file_manager = FileManager()
