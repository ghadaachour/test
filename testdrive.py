
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_DRIVE_API_KEY")
FOLDER_ID = "1Y9WT1gtUmWT7dBj8POqMeweU9sgQPEIo"

url = "https://www.googleapis.com/drive/v3/files"

params = {
    "key": API_KEY,
    "q": f"'{FOLDER_ID}' in parents and trashed = false",
    "fields": "files(id,name,mimeType,parents)",
    "pageSize": 100
}

response = requests.get(url, params=params, timeout=30)

print("HTTP STATUS:", response.status_code)

try:
    data = response.json()
    print("GOOGLE DRIVE RESPONSE:")
    print(data)
except ValueError:
    print(response.text)
