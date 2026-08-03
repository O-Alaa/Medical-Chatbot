from typing import Any

import requests

from config import (
    API_URL,
    ASK_TIMEOUT_SECONDS,
    UPLOAD_TIMEOUT_SECONDS,
)


class APIError(RuntimeError):
    """Raised when communication with the backend fails."""


def extract_error_message(response: requests.Response) -> str:
    """Extract a readable error message from the backend response."""

    try:
        response_data: Any = response.json()
    except ValueError:
        response_data = response.text

    if isinstance(response_data, dict):
        error_message = (
            response_data.get("error")
            or response_data.get("detail")
            or response_data.get("message")
        )

        if error_message:
            return str(error_message)

    if isinstance(response_data, str) and response_data.strip():
        return response_data.strip()

    return (
        f"The backend returned HTTP status "
        f"{response.status_code}."
    )


def upload_pdfs_api(files) -> dict:
    """Upload PDF files to the FastAPI backend."""

    files_payload = []

    for uploaded_file in files:
        files_payload.append(
            (
                "files",
                (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf",
                ),
            )
        )

    try:
        response = requests.post(
            f"{API_URL}/upload_pdfs/",
            files=files_payload,
            timeout=(30, UPLOAD_TIMEOUT_SECONDS),
        )

    except requests.Timeout as error:
        raise APIError(
            "The document upload timed out. Try uploading fewer "
            "or smaller PDF files."
        ) from error

    except requests.ConnectionError as error:
        raise APIError(
            "The backend could not be reached. The Render service "
            "may still be waking up."
        ) from error

    except requests.RequestException as error:
        raise APIError(
            f"An upload error occurred: {error}"
        ) from error

    if not response.ok:
        raise APIError(extract_error_message(response))

    try:
        return response.json()

    except ValueError as error:
        raise APIError(
            "The backend returned an invalid JSON response."
        ) from error


def ask_question(question: str) -> dict:
    """Send a medical question to the FastAPI backend."""

    try:
        response = requests.post(
            f"{API_URL}/ask/",
            data={"question": question},
            timeout=(30, ASK_TIMEOUT_SECONDS),
        )

    except requests.Timeout as error:
        raise APIError(
            "The answer took too long to generate. Please try again."
        ) from error

    except requests.ConnectionError as error:
        raise APIError(
            "The backend could not be reached. The free Render "
            "service may still be starting."
        ) from error

    except requests.RequestException as error:
        raise APIError(
            f"A request error occurred: {error}"
        ) from error

    if not response.ok:
        raise APIError(extract_error_message(response))

    try:
        return response.json()

    except ValueError as error:
        raise APIError(
            "The backend returned an invalid JSON response."
        ) from error
