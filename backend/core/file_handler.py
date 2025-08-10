"""
Enhanced file handling with better error handling and validation
"""
import pandas as pd
import io
import logging
from typing import Dict, List, Union
import uuid
import os
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)


class FileManager:
    """Manages uploaded files and their processing"""
    
    def __init__(self):
        self.files_storage = {}  # In-memory storage for demo
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        self._load_existing_files()
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return file ID"""
        # Clear old files from memory for performance optimization
        self._cleanup_old_files()

        file_id = str(uuid.uuid4())

        # Save file to disk for persistence
        file_path = self.upload_dir / f"{file_id}_{filename}"
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Load and store sheets in memory for quick access
        try:
            sheets = self._load_file_from_bytes(file_content, filename)

            # Auto-fix column names (especially Yazaki PN → YAZAKI PN)
            sheets = self._auto_fix_column_names(sheets)

            self.files_storage[file_id] = {
                "filename": filename,
                "file_path": str(file_path),
                "sheets": sheets,
                "processed_sheets": {},
                "upload_time": pd.Timestamp.now()  # Track upload time for cleanup
            }

            logger.info(f"File uploaded and cached: {filename} (ID: {file_id})")
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

    def _auto_fix_column_names(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Auto-fix common column name issues"""
        fixed_sheets = {}

        for sheet_name, df in sheets.items():
            df_copy = df.copy()

            # Fix column names
            new_columns = []
            changes_made = []

            for i, col in enumerate(df_copy.columns):
                original_col = col

                # Fix Yazaki PN → YAZAKI PN (case insensitive)
                if str(col).lower().strip() in ['yazaki pn', 'yazaki_pn', 'yazakipn']:
                    new_col = 'YAZAKI PN'
                    new_columns.append(new_col)
                    if original_col != new_col:
                        changes_made.append(f"'{original_col}' → '{new_col}'")

                # Fix other common variations
                elif str(col).lower().strip() in ['yazaki PN', 'YAZAKI_PN', 'YAZAKIPN']:
                    new_col = 'YAZAKI PN'
                    new_columns.append(new_col)
                    if original_col != new_col:
                        changes_made.append(f"'{original_col}' → '{new_col}'")

                # Keep original column name if no fix needed
                else:
                    new_columns.append(col)

            # Apply column name changes
            df_copy.columns = new_columns

            # Log changes
            if changes_made:
                logger.info(f"Auto-fixed column names in sheet '{sheet_name}': {', '.join(changes_made)}")

            fixed_sheets[sheet_name] = df_copy

        return fixed_sheets
    
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
            # Fill NaN values with empty strings to avoid JSON serialization issues
            df_preview = df.head(rows).fillna('')
            previews[sheet_name] = df_preview.to_dict('records')
        return previews
    
    def cleanup_file(self, file_id: str):
        """Remove file from storage and disk"""
        if file_id in self.files_storage:
            file_path = Path(self.files_storage[file_id]["file_path"])
            if file_path.exists():
                file_path.unlink()
            del self.files_storage[file_id]

    def _cleanup_old_files(self, max_files: int = 5, max_age_hours: int = 24):
        """Clean up old files from memory to optimize performance"""
        if len(self.files_storage) <= max_files:
            return

        current_time = pd.Timestamp.now()
        files_to_remove = []

        # Find files older than max_age_hours
        for file_id, file_info in self.files_storage.items():
            upload_time = file_info.get('upload_time', current_time)
            age_hours = (current_time - upload_time).total_seconds() / 3600

            if age_hours > max_age_hours:
                files_to_remove.append(file_id)

        # If still too many files, remove oldest ones
        if len(self.files_storage) - len(files_to_remove) > max_files:
            # Sort by upload time and remove oldest
            sorted_files = sorted(
                self.files_storage.items(),
                key=lambda x: x[1].get('upload_time', pd.Timestamp.now())
            )

            additional_removals = len(self.files_storage) - len(files_to_remove) - max_files
            for i in range(additional_removals):
                file_id = sorted_files[i][0]
                if file_id not in files_to_remove:
                    files_to_remove.append(file_id)

        # Remove old files
        for file_id in files_to_remove:
            self._remove_file_from_cache(file_id)

        if files_to_remove:
            logger.info(f"Cleaned up {len(files_to_remove)} old files from cache for performance optimization")

    def _remove_file_from_cache(self, file_id: str):
        """Remove a specific file from cache"""
        if file_id in self.files_storage:
            file_info = self.files_storage[file_id]

            # Remove from memory
            del self.files_storage[file_id]

            # Optionally remove from disk (uncomment if needed)
            # file_path = Path(file_info["file_path"])
            # if file_path.exists():
            #     file_path.unlink()

            logger.debug(f"Removed file {file_id} from cache")

    def clear_all_cache(self):
        """Clear all cached files for performance optimization"""
        file_count = len(self.files_storage)
        self.files_storage.clear()
        logger.info(f"Cleared all {file_count} files from cache for performance optimization")

    def _load_existing_files(self):
        """Load existing files from upload directory on startup"""
        try:
            for file_path in self.upload_dir.glob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.csv', '.xlsx', '.xls']:
                    # Extract file_id and original filename from the saved filename
                    # Format: {file_id}_{original_filename}
                    filename_parts = file_path.name.split('_', 1)
                    if len(filename_parts) == 2:
                        file_id, original_filename = filename_parts

                        try:
                            # Load the file
                            with open(file_path, 'rb') as f:
                                file_content = f.read()

                            sheets = self._load_file_from_bytes(file_content, original_filename)
                            sheets = self._auto_fix_column_names(sheets)

                            self.files_storage[file_id] = {
                                "filename": original_filename,
                                "file_path": str(file_path),
                                "sheets": sheets,
                                "processed_sheets": {},
                                "upload_time": pd.Timestamp.fromtimestamp(file_path.stat().st_mtime)
                            }

                            logger.info(f"Loaded existing file: {original_filename} (ID: {file_id})")

                        except Exception as e:
                            logger.warning(f"Failed to load existing file {file_path}: {e}")

            logger.info(f"Loaded {len(self.files_storage)} existing files from upload directory")

        except Exception as e:
            logger.error(f"Error loading existing files: {e}")


# Global file manager instance
file_manager = FileManager()
