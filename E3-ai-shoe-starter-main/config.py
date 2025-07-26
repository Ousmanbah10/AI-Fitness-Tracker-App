import os
from dotenv import load_dotenv
import sys

# Print debugging info

# Try to read the file directly
env_path = os.path.join(os.getcwd(), '.env')

try:
    # Read the file content directly
    with open(env_path, 'r') as f:
        env_content = f.read()
   
    # Manual parsing
    for line in env_content.splitlines():
        if line and not line.startswith('#'):
            try:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
               
            except Exception as e:
                print(f"Error parsing line '{line}': {e}")
except Exception as e:
    print(f"Error reading .env file: {e}")

# Try loading with dotenv again
load_dotenv(env_path, override=True)



def get_config():
    """Retrieves Auth0 configuration from environment variables."""
    domain = os.environ.get("AUTH0_DOMAIN")
    client_id = os.environ.get("AUTH0_CLIENT_ID")
    client_secret = os.environ.get("AUTH0_CLIENT_SECRET")
    callback_url = os.environ.get("AUTH0_CALLBACK_URL", "http://localhost:8080/callback")
    
    
    
    if not all([domain, client_id, client_secret]):
        if os.getenv("CI") == "true":
            return {
                "AUTH0_DOMAIN": "test-auth0-domain",
                "AUTH0_CLIENT_ID": "test-client-id",
                "AUTH0_CLIENT_SECRET": "test-secret",
                "AUTH0_CALLBACK_URL": "http://localhost:8080/callback"
            }

        raise ValueError(
            "Missing Auth0 configuration. "
            "Please set AUTH0_DOMAIN, AUTH0_CLIENT_ID, and AUTH0_CLIENT_SECRET environment variables.")
   
    return {
        "AUTH0_DOMAIN": domain,
        "AUTH0_CLIENT_ID": client_id,
        "AUTH0_CLIENT_SECRET": client_secret,
        "AUTH0_CALLBACK_URL": callback_url,
    }

config = get_config()
