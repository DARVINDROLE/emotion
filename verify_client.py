import os
from google_auth_oauthlib.flow import Flow

def verify_client():
    try:
        flow = Flow.from_client_secrets_file(
            "client_secret.json",
            scopes=['openid'],
            redirect_uri="http://127.0.0.1:5000/callback"
        )
        print("✅ Using correct client ID:", flow.client_config["client_id"])
    except Exception as e:
        print("❌ Error:", str(e))
        if "deleted_client" in str(e):
            print("🔥 The client ID has been deleted in Google Cloud Console")

if __name__ == "__main__":
    verify_client()