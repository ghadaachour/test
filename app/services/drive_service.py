
import os
import re
import requests

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_DRIVE_API_KEY")

DRIVE_API_URL = "https://www.googleapis.com/drive/v3"

SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}


class DriveServiceError(Exception):
    """Custom exception for Google Drive service errors."""
    pass


def extract_folder_id(url: str) -> str:
    """Extract and validate a Google Drive folder ID."""

    if not isinstance(url, str):
        raise DriveServiceError("The Google Drive URL must be a string.")

    match = re.search(
        r"(?:https?://)?(?:drive\.google\.com)/drive/(?:u/\d+/)?folders/([a-zA-Z0-9_-]+)",
        url.strip()
    )

    if not match:
        raise DriveServiceError("Invalid Google Drive folder URL.")

    return match.group(1)


def list_files(folder_id: str) -> list:
    """List supported documents in a public Google Drive folder."""

    if not API_KEY:
        raise DriveServiceError("Google Drive API key is missing.")

    if not folder_id:
        raise DriveServiceError("Folder ID is missing.")

    files = []
    page_token = None

    while True:
        params = {
            "key": API_KEY,
            "q": f"'{folder_id}' in parents and trashed = false",
            "fields": "nextPageToken,files(id,name,mimeType,size)",
            "pageSize": 1000,
            "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true",
        }

        if page_token:
            params["pageToken"] = page_token

        try:
            response = requests.get(
                f"{DRIVE_API_URL}/files",
                params=params,
                timeout=30
            )
            response.raise_for_status()

        except requests.RequestException as exc:
            raise DriveServiceError(
                f"Unable to retrieve Google Drive files: {exc}"
            ) from exc

        data = response.json()

        for file in data.get("files", []):
            mime = file.get("mimeType")

            if mime in SUPPORTED_MIME_TYPES:
                files.append({
                    "id": file["id"],
                    "name": file["name"],
                    "mimeType": mime,
                    "size": int(file.get("size", 0)),
                })

        page_token = data.get("nextPageToken")

        if not page_token:
            break

    return files


def download_file(file_id: str) -> bytes:
    """Download a public Google Drive file."""

    if not API_KEY:
        raise DriveServiceError("Google Drive API key is missing.")

    if not file_id:
        raise DriveServiceError("File ID is missing.")

    try:
        response = requests.get(
            f"{DRIVE_API_URL}/files/{file_id}",
            params={
                "alt": "media",
                "key": API_KEY,
                "supportsAllDrives": "true",
            },
            timeout=60,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise DriveServiceError(
            f"Unable to download Google Drive file: {exc}"
        ) from exc

    return response.content
