"""
SharePoint Connection Test Script
Test different authentication methods for SharePoint access
"""
import os
import sys

# Add the backend path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_sharepoint_connection():
    """Test SharePoint connection with different methods"""
    
    # Configuration
    site_url = "https://uitacma.sharepoint.com/sites/YAZAKIInternship"
    folder_path = "/sites/YAZAKIInternship/Shared Documents"
    
    print("🔧 SharePoint Connection Test")
    print("=" * 50)
    print(f"Site URL: {site_url}")
    print(f"Folder Path: {folder_path}")
    print()
    
    # Get credentials from user
    username = input("Enter your SharePoint username (email): ")
    password = input("Enter your SharePoint password: ")
    
    print("\n🔐 Testing authentication methods...")
    print("-" * 40)
    
    # Test Method 1: Basic Authentication
    print("\n1️⃣ Testing Basic Authentication...")
    try:
        from office365.runtime.auth.authentication_context import AuthenticationContext
        from office365.sharepoint.client_context import ClientContext
        
        ctx_auth = AuthenticationContext(site_url)
        if ctx_auth.acquire_token_for_user(username, password):
            ctx = ClientContext(site_url, ctx_auth)
            web = ctx.web
            ctx.load(web)
            ctx.execute_query()
            print(f"✅ Basic Authentication SUCCESS! Site: {web.title}")
            
            # Test file listing
            try:
                folder = ctx.web.get_folder_by_server_relative_url(folder_path)
                ctx.load(folder)
                ctx.execute_query()
                
                files = folder.files
                ctx.load(files)
                ctx.execute_query()
                
                print(f"📁 Found {len(files)} files in folder")
                for file in files[:5]:  # Show first 5 files
                    print(f"  - {file.name}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more files")
                
                return True
                
            except Exception as folder_error:
                print(f"⚠️ Basic auth worked but folder access failed: {folder_error}")
                return False
        else:
            print("❌ Basic Authentication FAILED")
    except Exception as e:
        print(f"❌ Basic Authentication ERROR: {e}")
    
    # Test Method 2: UserCredential
    print("\n2️⃣ Testing UserCredential Authentication...")
    try:
        from office365.runtime.auth.user_credential import UserCredential
        from office365.sharepoint.client_context import ClientContext
        
        credentials = UserCredential(username, password)
        ctx = ClientContext(site_url).with_credentials(credentials)
        
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        print(f"✅ UserCredential Authentication SUCCESS! Site: {web.title}")
        
        # Test file listing
        try:
            folder = ctx.web.get_folder_by_server_relative_url(folder_path)
            ctx.load(folder)
            ctx.execute_query()
            
            files = folder.files
            ctx.load(files)
            ctx.execute_query()
            
            print(f"📁 Found {len(files)} files in folder")
            for file in files[:5]:  # Show first 5 files
                print(f"  - {file.name}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more files")
            
            return True
            
        except Exception as folder_error:
            print(f"⚠️ UserCredential auth worked but folder access failed: {folder_error}")
            return False
            
    except Exception as e:
        print(f"❌ UserCredential Authentication ERROR: {e}")
    
    # Test Method 3: MSAL Interactive (if available)
    print("\n3️⃣ Testing MSAL Interactive Authentication...")
    try:
        import msal
        from office365.sharepoint.client_context import ClientContext
        
        # Configuration for uit.ac.ma tenant
        client_id = "9bc3ab49-b65d-410a-85ad-de819febfddc"
        authority = "https://login.microsoftonline.com/uit.ac.ma"
        scopes = ["https://uitacma.sharepoint.com/.default"]
        
        app = msal.PublicClientApplication(
            client_id=client_id,
            authority=authority
        )
        
        print("🌐 Opening browser for authentication...")
        result = app.acquire_token_interactive(
            scopes=scopes,
            login_hint=username
        )
        
        if "access_token" in result:
            ctx = ClientContext(site_url).with_access_token(result["access_token"])
            
            web = ctx.web
            ctx.load(web)
            ctx.execute_query()
            print(f"✅ MSAL Authentication SUCCESS! Site: {web.title}")
            
            # Test file listing
            try:
                folder = ctx.web.get_folder_by_server_relative_url(folder_path)
                ctx.load(folder)
                ctx.execute_query()
                
                files = folder.files
                ctx.load(files)
                ctx.execute_query()
                
                print(f"📁 Found {len(files)} files in folder")
                for file in files[:5]:  # Show first 5 files
                    print(f"  - {file.name}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more files")
                
                return True
                
            except Exception as folder_error:
                print(f"⚠️ MSAL auth worked but folder access failed: {folder_error}")
                return False
        else:
            error_msg = result.get('error_description', 'Unknown error')
            print(f"❌ MSAL Authentication FAILED: {error_msg}")
            
    except ImportError:
        print("❌ MSAL library not available")
    except Exception as e:
        print(f"❌ MSAL Authentication ERROR: {e}")
    
    print("\n❌ All authentication methods failed!")
    print("\n💡 Troubleshooting suggestions:")
    print("1. Verify your SharePoint credentials")
    print("2. Check if you have access to the SharePoint site")
    print("3. Ensure the site URL is correct")
    print("4. Contact your IT administrator for permissions")
    print("5. Try accessing the SharePoint site in a web browser first")
    
    return False

if __name__ == "__main__":
    try:
        success = test_sharepoint_connection()
        if success:
            print("\n🎉 SharePoint connection test SUCCESSFUL!")
            print("You can now use the SharePoint integration in the ETL tool.")
        else:
            print("\n❌ SharePoint connection test FAILED!")
            print("Please resolve the issues before using SharePoint integration.")
    except KeyboardInterrupt:
        print("\n\n⏹️ Test cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
