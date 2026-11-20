
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.drive_service import (
    extract_folder_id,
    list_files,
    download_file,
    DriveServiceError
)
from app.services.processing_service import process_document


router = APIRouter(prefix="/api", tags=["Drive-to-Text"])


class DriveFolderRequest(BaseModel):
    folder_url: str = Field(
        ...,
        description="Public Google Drive folder URL"
    )


class ProcessRequest(BaseModel):
    folder_url: str
    file_ids: list[str] = Field(
        ...,
        min_length=1,
        description="IDs of the selected files"
    )


@router.post("/drive/files")
def get_drive_files(request: DriveFolderRequest):
    """
    List supported PDF and image files in a public Drive folder.
    """

    try:
        folder_id = extract_folder_id(request.folder_url)
        files = list_files(folder_id)

        return {
            "folder_id": folder_id,
            "total_files": len(files),
            "files": files
        }

    except DriveServiceError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("/drive/process")
def process_drive_files(request: ProcessRequest):
    """
    Download and process selected files from a public Drive folder.
    """

    try:
        folder_id = extract_folder_id(request.folder_url)
        available_files = list_files(folder_id)

    except DriveServiceError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # Ensure that selected files belong to the provided folder
    files_by_id = {
        file["id"]: file for file in available_files
    }

    unknown_ids = [
        file_id for file_id in request.file_ids
        if file_id not in files_by_id
    ]

    if unknown_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Files not found in this folder: {unknown_ids}"
        )

    results = []

    for file_id in request.file_ids:
        file_info = files_by_id[file_id]

        try:
            content = download_file(file_id)

            result = process_document(
                file_name=file_info["name"],
                mime_type=file_info["mimeType"],
                content=content
            )

        except Exception as error:
            result = {
                "file_name": file_info["name"],
                "status": "failed",
                "method": None,
                "text": "",
                "error": str(error)
            }

        results.append(result)

    successful = sum(
        1 for result in results
        if result["status"] == "done"
    )

    failed = len(results) - successful

    return {
        "folder_id": folder_id,
        "total_files": len(results),
        "successful": successful,
        "failed": failed,
        "results": results
    }
