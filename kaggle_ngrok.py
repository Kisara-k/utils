!pip install fastapi uvicorn pyngrok nest-asyncio -q

from kaggle_secrets import UserSecretsClient
from pyngrok import ngrok
from fastapi import FastAPI
import nest_asyncio
import uvicorn
import threading

# Set up ngrok
NGROK_API_KEY = UserSecretsClient().get_secret("ngrok-auth")
ngrok.set_auth_token(NGROK_API_KEY)

tunnel = ngrok.connect(8000)  # 1 instance and 3 ports max on free version

# Create FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Apply nest_asyncio to run in notebook
nest_asyncio.apply()

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

thread = threading.Thread(target=run_server, daemon=True)
thread.start()

print("FastAPI is live at:", tunnel.public_url)




import requests

# Test the endpoint
response = requests.get(tunnel.public_url)
print("Test response:", response.json())
