"""
API client for communicating with FastAPI backend
"""
import requests
import streamlit as st
from typing import Dict, List, Any, Optional
import io


class ETLAPIClient:
    """Client for ETL API communication"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def upload_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Upload file to backend"""
        try:
            files = {"file": (filename, io.BytesIO(file_content), "application/octet-stream")}
            response = self.session.post(f"{self.base_url}/upload", files=files)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Upload failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def preview_sheets(self, file_id: str, sheet_names: List[str]) -> Dict[str, Any]:
        """Get sheet previews"""
        try:
            data = {"file_id": file_id, "sheet_names": sheet_names}
            response = self.session.post(f"{self.base_url}/preview", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Preview failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def clean_data(self, file_id: str, master_sheet: str, target_sheet: str) -> Dict[str, Any]:
        """Clean data"""
        try:
            data = {
                "file_id": file_id,
                "master_sheet": master_sheet,
                "target_sheet": target_sheet
            }
            response = self.session.post(f"{self.base_url}/clean", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Cleaning failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def suggest_column(self, input_name: str, available_columns: List[str]) -> Dict[str, Any]:
        """Get column suggestion"""
        try:
            data = {
                "input_name": input_name,
                "available_columns": available_columns
            }
            response = self.session.post(f"{self.base_url}/suggest-column", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Column suggestion failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_lookup_columns(self, file_id: str, sheet_name: str) -> Dict[str, Any]:
        """Get available lookup columns"""
        try:
            response = self.session.get(f"{self.base_url}/columns/{file_id}/{sheet_name}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Get columns failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def perform_lookup(self, file_id: str, master_sheet: str, target_sheet: str, 
                      lookup_column: str, key_column: str = "YAZAKI PN") -> Dict[str, Any]:
        """Perform lookup operation"""
        try:
            data = {
                "file_id": file_id,
                "master_sheet": master_sheet,
                "target_sheet": target_sheet,
                "lookup_column": lookup_column,
                "key_column": key_column
            }
            response = self.session.post(f"{self.base_url}/lookup", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Lookup failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def download_data(self, file_id: str, sheet_name: str) -> Optional[bytes]:
        """Download processed data"""
        try:
            response = self.session.get(f"{self.base_url}/download/{file_id}/{sheet_name}")
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            st.error(f"Download failed: {str(e)}")
            return None
    
    def process_master_updates(self, file_id: str, master_sheet: str, target_sheet: str,
                              lookup_column: str) -> Dict[str, Any]:
        """Process Master BOM updates based on activation status"""
        try:
            data = {
                "file_id": file_id,
                "master_sheet": master_sheet,
                "target_sheet": target_sheet,
                "lookup_column": lookup_column
            }
            response = self.session.post(f"{self.base_url}/process-updates", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Master BOM update failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def health_check(self) -> bool:
        """Check if API is available"""
        try:
            response = self.session.get(f"{self.base_url}/")
            return response.status_code == 200
        except:
            return False


# Global API client instance
api_client = ETLAPIClient()
