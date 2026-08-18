"""Small Atlas Cloud client for asynchronous speech-to-text jobs."""

from __future__ import annotations

import mimetypes
import os
import re
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

API_BASE = "https://api.atlascloud.ai/api/v1"
MODEL = "xai/stt-v1"
MAX_UPLOAD_BYTES = 500 * 1024 * 1024
MAX_POLL_ATTEMPTS = 120
RETRYABLE_GET_STATUSES = {429, 500, 502, 503, 504}
TERMINAL_FAILURE_STATUSES = {"failed", "canceled", "cancelled", "timeout"}
PENDING_STATUSES = {"created", "queued", "starting", "processing"}


class AtlasError(RuntimeError):
    """Raised when Atlas Cloud rejects or cannot complete a request."""


def _api_key() -> str:
    value = os.getenv("ATLASCLOUD_API_KEY", "").strip()
    if not value:
        raise AtlasError("ATLASCLOUD_API_KEY is not set")
    return value


def _payload(response: requests.Response) -> dict[str, Any]:
    response.raise_for_status()
    try:
        payload = response.json()
    except ValueError as exc:
        raise AtlasError("Atlas Cloud returned a non-JSON response") from exc
    if payload.get("code") not in (0, 200):
        message = payload.get("message") or "request failed"
        raise AtlasError(f"Atlas Cloud request failed: {message}")
    return payload


def _https_url(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise AtlasError(f"Atlas Cloud response is missing {field}")
    parsed = urlparse(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise AtlasError(f"Atlas Cloud returned an unsafe {field}")
    return value


def upload_audio(path: Path, session: requests.Session | None = None) -> str:
    """Upload one local media file without retrying the POST."""
    size = path.stat().st_size
    if size == 0:
        raise AtlasError("Input file is empty")
    if size > MAX_UPLOAD_BYTES:
        raise AtlasError("Input file exceeds the 500 MB Atlas Cloud limit")

    client = session or requests.Session()
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    with path.open("rb") as handle:
        response = client.post(
            f"{API_BASE}/model/uploadMedia",
            headers={"Authorization": f"Bearer {_api_key()}"},
            files={"file": (path.name, handle, mime)},
            timeout=(10, 120),
        )
    data = _payload(response).get("data") or {}
    return _https_url(data.get("download_url"), "download URL")


def submit_transcription(
    audio_url: str,
    language: str | None = None,
    session: requests.Session | None = None,
) -> str:
    """Submit one transcription job without retrying the POST."""
    request: dict[str, Any] = {
        "model": MODEL,
        "audio": _https_url(audio_url, "audio URL"),
    }
    if language:
        request["language"] = language

    client = session or requests.Session()
    response = client.post(
        f"{API_BASE}/model/generateAudio",
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        },
        json=request,
        timeout=(10, 60),
    )
    data = _payload(response).get("data") or {}
    prediction_id = data.get("id")
    if not isinstance(prediction_id, str) or not re.fullmatch(
        r"[A-Za-z0-9_-]+", prediction_id
    ):
        raise AtlasError("Atlas Cloud response is missing a valid prediction ID")
    return prediction_id


def poll_transcription(
    prediction_id: str,
    session: requests.Session | None = None,
    sleep: Callable[[float], None] = time.sleep,
    max_attempts: int = MAX_POLL_ATTEMPTS,
) -> dict[str, Any]:
    """Poll one fixed Atlas endpoint with bounded retries for GET only."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", prediction_id):
        raise AtlasError("Invalid prediction ID")
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")

    client = session or requests.Session()
    headers = {"Authorization": f"Bearer {_api_key()}"}
    for attempt in range(max_attempts):
        sleep(min(2 ** attempt, 8))
        response = client.get(
            f"{API_BASE}/model/prediction/{prediction_id}",
            headers=headers,
            timeout=(10, 60),
        )
        if response.status_code in RETRYABLE_GET_STATUSES:
            if attempt + 1 == max_attempts:
                response.raise_for_status()
            continue

        data = _payload(response).get("data") or {}
        status = str(data.get("status") or "").lower()
        if status in {"completed", "succeeded"}:
            result = data.get("stt_result")
            if not isinstance(result, dict) or not isinstance(result.get("text"), str):
                raise AtlasError(
                    "Completed Atlas Cloud job has no transcription result"
                )
            return result
        if status in TERMINAL_FAILURE_STATUSES:
            detail = data.get("error") or "unknown error"
            raise AtlasError(f"Atlas Cloud transcription {status}: {detail}")
        if status not in PENDING_STATUSES:
            detail = status or "empty"
            raise AtlasError(f"Atlas Cloud returned unknown status: {detail}")

    raise AtlasError("Atlas Cloud transcription timed out")


def _joined_words(words: list[dict[str, Any]]) -> str:
    text = " ".join(str(word["text"]).strip() for word in words).strip()
    return re.sub(r"\s+([,.;:!?%\)\]\}，。！？；：])", r"\1", text)


def words_to_segments(
    words: list[dict[str, Any]],
    max_duration: float = 8.0,
    max_chars: int = 80,
) -> list[dict[str, Any]]:
    """Group word timestamps into subtitle-sized segments."""
    segments: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []

    for word in words:
        text = str(word.get("text") or "").strip()
        start = word.get("start")
        end = word.get("end")
        if (
            not text
            or not isinstance(start, (int, float))
            or not isinstance(end, (int, float))
        ):
            continue
        if start < 0 or end < start:
            continue

        candidate = [*current, {"text": text, "start": float(start), "end": float(end)}]
        too_long = bool(current) and (
            candidate[-1]["end"] - candidate[0]["start"] > max_duration
            or len(_joined_words(candidate)) > max_chars
        )
        if too_long:
            segments.append(
                {
                    "start": current[0]["start"],
                    "end": current[-1]["end"],
                    "text": _joined_words(current),
                }
            )
            current = []

        current.append({"text": text, "start": float(start), "end": float(end)})
        if re.search(r"[.!?。！？]$", text):
            segments.append(
                {
                    "start": current[0]["start"],
                    "end": current[-1]["end"],
                    "text": _joined_words(current),
                }
            )
            current = []

    if current:
        segments.append(
            {
                "start": current[0]["start"],
                "end": current[-1]["end"],
                "text": _joined_words(current),
            }
        )
    return segments


def transcribe_file(
    path: Path,
    language: str | None = None,
    session: requests.Session | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Upload, submit once, and poll a local file through Atlas Cloud."""
    client = session or requests.Session()
    audio_url = upload_audio(path, session=client)
    prediction_id = submit_transcription(audio_url, language=language, session=client)
    result = poll_transcription(prediction_id, session=client, sleep=sleep)
    words = result.get("words") if isinstance(result.get("words"), list) else []
    return {
        "text": result["text"],
        "language": result.get("language_code") or result.get("language") or "unknown",
        "duration": result.get("duration"),
        "words": words,
        "segments": words_to_segments(words),
    }
