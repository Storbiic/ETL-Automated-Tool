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

    def list_sharepoint_files(self, site_url: str, username: str, password: str, folder_path: str) -> Dict[str, Any]:
        """List files in SharePoint folder"""
        try:
            data = {
                "site_url": site_url,
                "username": username,
                "password": password,
                "folder_path": folder_path
            }
            response = self.session.post(f"{self.base_url}/sharepoint/list-files", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"SharePoint file listing failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def download_sharepoint_file(self, site_url: str, username: str, password: str, folder_path: str, file_name: str) -> Dict[str, Any]:
        """Download file from SharePoint"""
        try:
            data = {
                "site_url": site_url,
                "username": username,
                "password": password,
                "folder_path": folder_path,
                "file_name": file_name
            }
            response = self.session.post(f"{self.base_url}/sharepoint/download", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"SharePoint download failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def preview_processing_changes(self, file_id: str, master_sheet: str, target_sheet: str, lookup_column: str, key_column: str) -> Dict[str, Any]:
        """Preview changes before applying them"""
        try:
            data = {
                "file_id": file_id,
                "master_sheet": master_sheet,
                "target_sheet": target_sheet,
                "lookup_column": lookup_column,
                "key_column": key_column
            }
            response = self.session.post(f"{self.base_url}/processing/preview", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Processing preview failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def upload_to_sharepoint(self, site_url: str, username: str, password: str, folder_path: str, file_name: str, file_id: str, create_backup: bool = True) -> Dict[str, Any]:
        """Upload processed file to SharePoint"""
        try:
            data = {
                "site_url": site_url,
                "username": username,
                "password": password,
                "folder_path": folder_path,
                "file_name": file_name,
                "file_id": file_id,
                "create_backup": create_backup
            }
            response = self.session.post(f"{self.base_url}/sharepoint/upload", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"SharePoint upload failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def rollback_sharepoint_file(self, site_url: str, username: str, password: str, folder_path: str, original_file: str, backup_file: str) -> Dict[str, Any]:
        """Rollback SharePoint file to previous version"""
        try:
            data = {
                "site_url": site_url,
                "username": username,
                "password": password,
                "folder_path": folder_path,
                "original_file": original_file,
                "backup_file": backup_file
            }
            response = self.session.post(f"{self.base_url}/sharepoint/rollback", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"SharePoint rollback failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_file_history(self, site_url: str, username: str, password: str, folder_path: str, file_name: str) -> Dict[str, Any]:
        """Get version history for SharePoint file"""
        try:
            params = {
                "site_url": site_url,
                "username": username,
                "password": password,
                "folder_path": folder_path
            }
            response = self.session.get(f"{self.base_url}/sharepoint/history/{file_name}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"File history retrieval failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def analyze_column_distribution(self, file_id: str, sheet_name: str, column_name: str) -> Dict[str, Any]:
        """Analyze distribution of values in a specific column"""
        try:
            data = {
                "file_id": file_id,
                "sheet_name": sheet_name,
                "column_name": column_name
            }
            response = self.session.post(f"{self.base_url}/analyze-column", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Column analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def analyze_column_distribution_filtered(self, file_id: str, master_sheet: str, target_sheet: str, column_name: str) -> Dict[str, Any]:
        """Analyze distribution of values in a specific column for items NOT in target sheet"""
        try:
            data = {
                "file_id": file_id,
                "master_sheet": master_sheet,
                "target_sheet": target_sheet,
                "column_name": column_name
            }
            response = self.session.post(f"{self.base_url}/analyze-column-filtered", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Filtered column analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def process_preexisting_items(self, file_id: str, master_sheet: str, target_sheet: str, column_name: str) -> Dict[str, Any]:
        """Process pre-existing items: Update X → D for items not in target sheet"""
        try:
            data = {
                "file_id": file_id,
                "master_sheet": master_sheet,
                "target_sheet": target_sheet,
                "column_name": column_name
            }
            response = self.session.post(f"{self.base_url}/process-preexisting", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Pre-existing items processing failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def export_logs(self, format: str) -> bytes:
        """Export logs in specified format"""
        try:
            response = self.session.get(f"{self.base_url}/logs/export/{format}")
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            st.error(f"Log export failed: {str(e)}")
            return b""

    def get_log_summary(self) -> Dict[str, Any]:
        """Get log summary"""
        try:
            response = self.session.get(f"{self.base_url}/logs/summary")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Log summary failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def clear_logs(self) -> Dict[str, Any]:
        """Clear all logs"""
        try:
            response = self.session.post(f"{self.base_url}/logs/clear")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Log clearing failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def rollback_preexisting_changes(self, file_id: str, master_sheet: str) -> Dict[str, Any]:
        """Rollback pre-existing items changes to original state"""
        try:
            data = {
                "file_id": file_id,
                "master_sheet": master_sheet
            }
            response = self.session.post(f"{self.base_url}/rollback-preexisting", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Rollback failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_rollback_status(self, file_id: str) -> Dict[str, Any]:
        """Check if rollback is available for a file"""
        try:
            response = self.session.get(f"{self.base_url}/rollback-status/{file_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Rollback status check failed: {str(e)}")
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

    def clear_cache(self) -> Dict[str, Any]:
        """Clear all cached files for performance optimization"""
        try:
            response = self.session.post(f"{self.base_url}/clear-cache")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Cache clearing failed: {str(e)}")
            return {"success": False, "error": str(e)}


# Global API client instance
api_client = ETLAPIClient()
