"""
SharePoint integration for ETL Automation Tool v2.0
Handles authentication and file operations with SharePoint
"""
import os
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
import tempfile
import shutil

logger = logging.getLogger(__name__)

class SharePointClient:
    """SharePoint client for file operations"""
    
    def __init__(self, site_url: str, username: str, password: str):
        self.site_url = site_url
        self.username = username
        self.password = password
        self.ctx = None
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """Authenticate with SharePoint using modern authentication only"""
        try:
            # For modern SharePoint tenants like uit.ac.ma, only MSAL works
            logger.info("🔐 Using modern authentication (MSAL) for uit.ac.ma tenant...")
            success = self._authenticate_custom_tenant()
            if success:
                return True

            logger.error("❌ Modern authentication failed")
            logger.info("💡 Your organization requires modern authentication. Please ensure:")
            logger.info("   1. You have access to the SharePoint site")
            logger.info("   2. You can authenticate through the browser popup")
            logger.info("   3. Your IT admin has enabled the required permissions")
            return False

        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def _authenticate_basic(self) -> bool:
        """Basic email + password authentication"""
        try:
            from office365.runtime.auth.authentication_context import AuthenticationContext
            from office365.sharepoint.client_context import ClientContext
            
            ctx_auth = AuthenticationContext(self.site_url)
            if ctx_auth.acquire_token_for_user(self.username, self.password):
                self.ctx = ClientContext(self.site_url, ctx_auth)
                
                # Test connection
                web = self.ctx.web
                self.ctx.load(web)
                self.ctx.execute_query()
                
                logger.info(f"✅ Basic authentication successful! Site: {web.title}")
                self.authenticated = True
                return True
            else:
                logger.warning("❌ Basic authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Basic authentication error: {e}")
            return False

    def _authenticate_username_password(self) -> bool:
        """Username/Password authentication with UserCredential"""
        try:
            from office365.runtime.auth.user_credential import UserCredential
            from office365.sharepoint.client_context import ClientContext

            # Create user credential
            credentials = UserCredential(self.username, self.password)
            self.ctx = ClientContext(self.site_url).with_credentials(credentials)

            # Test connection
            web = self.ctx.web
            self.ctx.load(web)
            self.ctx.execute_query()

            logger.info(f"✅ Username/Password authentication successful! Site: {web.title}")
            self.authenticated = True
            return True

        except Exception as e:
            logger.error(f"❌ Username/Password authentication error: {e}")
            return False

    def _authenticate_custom_tenant(self) -> bool:
        """Custom authentication for uit.ac.ma tenant"""
        try:
            import msal
            from office365.sharepoint.client_context import ClientContext

            # Custom configuration for uit.ac.ma tenant
            client_id = "9bc3ab49-b65d-410a-85ad-de819febfddc"  # SharePoint Online Client
            authority = "https://login.microsoftonline.com/uit.ac.ma"
            scopes = ["https://uitacma.sharepoint.com/.default"]

            app = msal.PublicClientApplication(
                client_id=client_id,
                authority=authority
            )

            logger.info("🌐 Opening browser for uit.ac.ma tenant authentication...")
            result = app.acquire_token_interactive(
                scopes=scopes,
                login_hint=self.username
            )

            if "access_token" in result:
                self.ctx = ClientContext(self.site_url).with_access_token(result["access_token"])

                # Test connection
                web = self.ctx.web
                self.ctx.load(web)
                self.ctx.execute_query()

                logger.info(f"✅ Custom tenant authentication successful! Site: {web.title}")
                self.authenticated = True
                return True
            else:
                error_msg = result.get('error_description', 'Unknown error')
                logger.error(f"❌ Custom tenant authentication failed: {error_msg}")
                return False

        except ImportError:
            logger.error("❌ MSAL library not installed. Install with: pip install msal")
            return False
        except Exception as e:
            logger.error(f"❌ Custom tenant authentication error: {e}")
            return False
    
    def _authenticate_msal(self) -> bool:
        """MSAL interactive authentication with proper tenant handling"""
        try:
            import msal
            from office365.sharepoint.client_context import ClientContext

            # Extract tenant from site URL
            import re
            tenant_match = re.search(r'https://([^.]+)\.sharepoint\.com', self.site_url)
            if not tenant_match:
                logger.error("❌ Could not extract tenant from site URL")
                return False

            tenant_name = tenant_match.group(1)

            # MSAL configuration with correct tenant
            client_id = "9bc3ab49-b65d-410a-85ad-de819febfddc"  # SharePoint Online Client
            authority = f"https://login.microsoftonline.com/{tenant_name}.onmicrosoft.com"
            scopes = [f"https://{tenant_name}.sharepoint.com/.default"]

            app = msal.PublicClientApplication(
                client_id=client_id,
                authority=authority
            )

            logger.info(f"🌐 Opening browser for authentication (tenant: {tenant_name})...")
            result = app.acquire_token_interactive(
                scopes=scopes,
                login_hint=self.username
            )

            if "access_token" in result:
                self.ctx = ClientContext(self.site_url).with_access_token(result["access_token"])

                # Test connection
                web = self.ctx.web
                self.ctx.load(web)
                self.ctx.execute_query()

                logger.info(f"✅ MSAL authentication successful! Site: {web.title}")
                self.authenticated = True
                return True
            else:
                error_msg = result.get('error_description', 'Unknown error')
                logger.error(f"❌ MSAL authentication failed: {error_msg}")
                return False

        except ImportError:
            logger.error("❌ MSAL library not installed. Install with: pip install msal")
            return False
        except Exception as e:
            logger.error(f"❌ MSAL authentication error: {e}")
            return False
    
    def list_files(self, folder_path: str) -> List[Dict[str, Any]]:
        """List files in SharePoint folder"""
        if not self.authenticated:
            raise Exception("Not authenticated with SharePoint")
        
        try:
            folder = self.ctx.web.get_folder_by_server_relative_url(folder_path)
            self.ctx.load(folder)
            self.ctx.execute_query()
            
            files = folder.files
            self.ctx.load(files)
            self.ctx.execute_query()
            
            file_list = []
            for file in files:
                file_list.append({
                    "name": file.name,
                    "size": file.length,
                    "modified": file.time_last_modified,
                    "url": file.server_relative_url
                })
            
            logger.info(f"📁 Found {len(file_list)} files in {folder_path}")
            return file_list
            
        except Exception as e:
            logger.error(f"❌ Error listing files: {e}")
            raise
    
    def download_file(self, folder_path: str, file_name: str, local_path: str) -> bool:
        """Download file from SharePoint to local path"""
        if not self.authenticated:
            raise Exception("Not authenticated with SharePoint")
        
        try:
            file_url = f"{folder_path}/{file_name}"
            
            with open(local_path, "wb") as local_file:
                file = self.ctx.web.get_file_by_server_relative_url(file_url)
                file.download(local_file).execute_query()
            
            logger.info(f"✅ Downloaded '{file_name}' to '{local_path}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error downloading file '{file_name}': {e}")
            return False
    
    def upload_file(self, folder_path: str, file_name: str, local_path: str) -> bool:
        """Upload file from local path to SharePoint"""
        if not self.authenticated:
            raise Exception("Not authenticated with SharePoint")
        
        try:
            with open(local_path, "rb") as local_file:
                content = local_file.read()
            
            folder = self.ctx.web.get_folder_by_server_relative_url(folder_path)
            folder.upload_file(file_name, content)
            self.ctx.execute_query()
            
            logger.info(f"✅ Uploaded '{local_path}' as '{file_name}' to SharePoint")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error uploading file '{file_name}': {e}")
            return False
    
    def create_backup(self, folder_path: str, file_name: str) -> str:
        """Create a backup of the file with timestamp"""
        if not self.authenticated:
            raise Exception("Not authenticated with SharePoint")

        try:
            # Generate backup filename
            name, ext = os.path.splitext(file_name)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{name}_Backup_{timestamp}{ext}"

            # Download original file
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, file_name)

            if self.download_file(folder_path, file_name, temp_file):
                # Upload as backup
                if self.upload_file(folder_path, backup_name, temp_file):
                    logger.info(f"🛡️ Backup created: '{backup_name}'")

                    # Cleanup
                    shutil.rmtree(temp_dir)
                    return backup_name

            # Cleanup on failure
            shutil.rmtree(temp_dir)
            return None

        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            return None

    def upload_processed_file(self, folder_path: str, file_name: str, local_path: str, create_backup: bool = True) -> Dict[str, Any]:
        """Upload processed file with optional backup creation"""
        if not self.authenticated:
            raise Exception("Not authenticated with SharePoint")

        try:
            result = {
                "success": False,
                "backup_created": None,
                "upload_timestamp": datetime.now().isoformat()
            }

            # Create backup first if requested
            if create_backup:
                backup_name = self.create_backup(folder_path, file_name)
                if backup_name:
                    result["backup_created"] = backup_name
                    logger.info(f"🛡️ Backup created before upload: {backup_name}")
                else:
                    logger.warning("⚠️ Could not create backup, proceeding with upload")

            # Upload the processed file
            if self.upload_file(folder_path, file_name, local_path):
                result["success"] = True
                logger.info(f"✅ Processed file uploaded successfully: {file_name}")
                return result
            else:
                raise Exception("Failed to upload processed file")

        except Exception as e:
            logger.error(f"❌ Error uploading processed file: {e}")
            result["error"] = str(e)
            return result

    def rollback_file(self, folder_path: str, original_file: str, backup_file: str) -> bool:
        """Rollback to a previous backup version"""
        if not self.authenticated:
            raise Exception("Not authenticated with SharePoint")

        try:
            # Download the backup file
            temp_dir = tempfile.mkdtemp()
            backup_temp = os.path.join(temp_dir, backup_file)

            if self.download_file(folder_path, backup_file, backup_temp):
                # Create a backup of current version before rollback
                current_backup = self.create_backup(folder_path, original_file)
                if current_backup:
                    logger.info(f"🛡️ Current version backed up as: {current_backup}")

                # Upload the backup as the current file (rollback)
                if self.upload_file(folder_path, original_file, backup_temp):
                    logger.info(f"🔄 Successfully rolled back {original_file} to {backup_file}")

                    # Cleanup
                    shutil.rmtree(temp_dir)
                    return True

            # Cleanup on failure
            shutil.rmtree(temp_dir)
            return False

        except Exception as e:
            logger.error(f"❌ Error during rollback: {e}")
            return False

    def get_file_history(self, folder_path: str, base_file_name: str) -> List[Dict[str, Any]]:
        """Get history of backups for a file"""
        if not self.authenticated:
            raise Exception("Not authenticated with SharePoint")

        try:
            files = self.list_files(folder_path)

            # Extract base name without extension
            base_name = os.path.splitext(base_file_name)[0]

            # Find all backup files for this base file
            backup_files = []
            for file in files:
                if file['name'].startswith(f"{base_name}_Backup_"):
                    backup_files.append({
                        "name": file['name'],
                        "size": file['size'],
                        "modified": file['modified'],
                        "type": "backup"
                    })

            # Add the original file
            for file in files:
                if file['name'] == base_file_name:
                    backup_files.insert(0, {
                        "name": file['name'],
                        "size": file['size'],
                        "modified": file['modified'],
                        "type": "current"
                    })
                    break

            # Sort by modification date (newest first)
            backup_files.sort(key=lambda x: x['modified'], reverse=True)

            logger.info(f"📋 Found {len(backup_files)} versions for {base_file_name}")
            return backup_files

        except Exception as e:
            logger.error(f"❌ Error getting file history: {e}")
            return []
