from google.auth import load_credentials_from_file
from google.oauth2 import service_account

# Define the credentials path
credentials_path = "/Users/chethangopal/Downloads/google_credentials.json"

# Define required scopes (matching your config.py)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    # Try loading credentials directly
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, 
        scopes=SCOPES
    )
    print("\n✅ Google API Authentication Details:")
    print(f"Service Account Email: {credentials.service_account_email}")
    print(f"Project ID: {credentials.project_id}\n")
    
except Exception as e:
    print(f"❌ Error: {e}") 