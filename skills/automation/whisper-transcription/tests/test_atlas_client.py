from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "atlas_client", SCRIPTS_DIR / "atlas_client.py"
)
assert MODULE_SPEC and MODULE_SPEC.loader
atlas_client = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(atlas_client)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, post_responses=None, get_responses=None):
        self.post_responses = list(post_responses or [])
        self.get_responses = list(get_responses or [])
        self.post_calls = []
        self.get_calls = []

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        return self.post_responses.pop(0)

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        return self.get_responses.pop(0)


class AtlasClientTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"ATLASCLOUD_API_KEY": "test-key"})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_transcribe_file_submits_each_post_once_and_polls(self):
        session = FakeSession(
            post_responses=[
                FakeResponse(
                    {
                        "code": 200,
                        "data": {
                            "download_url": "https://uploads.example/audio.wav"
                        },
                    }
                ),
                FakeResponse({"code": 200, "data": {"id": "prediction_123"}}),
            ],
            get_responses=[
                FakeResponse({"code": 200, "data": {"status": "processing"}}),
                FakeResponse(
                    {
                        "code": 200,
                        "data": {
                            "status": "completed",
                            "stt_result": {
                                "text": "Hello, world.",
                                "language_code": "eng",
                                "duration": 1.2,
                                "words": [
                                    {"text": "Hello", "start": 0.0, "end": 0.4},
                                    {"text": ",", "start": 0.4, "end": 0.5},
                                    {"text": "world.", "start": 0.6, "end": 1.2},
                                ],
                            },
                        },
                    }
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "speech.wav"
            audio.write_bytes(b"RIFFtest")
            result = atlas_client.transcribe_file(
                audio, language="en", session=session, sleep=lambda _: None
            )

        self.assertEqual(2, len(session.post_calls))
        self.assertEqual(2, len(session.get_calls))
        self.assertEqual("Hello, world.", result["text"])
        self.assertEqual("eng", result["language"])
        self.assertEqual(
            [{"start": 0.0, "end": 1.2, "text": "Hello, world."}],
            result["segments"],
        )
        submit_json = session.post_calls[1][1]["json"]
        self.assertEqual(
            {
                "model": "xai/stt-v1",
                "audio": "https://uploads.example/audio.wav",
                "language": "en",
            },
            submit_json,
        )

    def test_poll_retries_retryable_get_without_resubmission(self):
        session = FakeSession(
            get_responses=[
                FakeResponse({}, status_code=503),
                FakeResponse(
                    {
                        "code": 200,
                        "data": {
                            "status": "completed",
                            "stt_result": {"text": "Done", "words": []},
                        },
                    }
                ),
            ]
        )

        result = atlas_client.poll_transcription(
            "prediction_123", session=session, sleep=lambda _: None, max_attempts=2
        )

        self.assertEqual("Done", result["text"])
        self.assertEqual(0, len(session.post_calls))
        self.assertEqual(2, len(session.get_calls))

    def test_upload_rejects_non_https_download_url(self):
        session = FakeSession(
            post_responses=[
                FakeResponse({"code": 200, "data": {"download_url": "http://uploads.example/audio.wav"}})
            ]
        )

        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "speech.wav"
            audio.write_bytes(b"RIFFtest")
            with self.assertRaisesRegex(atlas_client.AtlasError, "unsafe download URL"):
                atlas_client.upload_audio(audio, session=session)

        self.assertEqual(1, len(session.post_calls))

    def test_words_to_segments_discards_invalid_words_and_splits_sentences(self):
        words = [
            {"text": "First", "start": 0, "end": 0.3},
            {"text": "sentence.", "start": 0.4, "end": 0.9},
            {"text": "", "start": 1.0, "end": 1.1},
            {"text": "Second", "start": 1.2, "end": 1.5},
            {"text": "part", "start": 1.6, "end": 1.9},
        ]

        self.assertEqual(
            [
                {"start": 0.0, "end": 0.9, "text": "First sentence."},
                {"start": 1.2, "end": 1.9, "text": "Second part"},
            ],
            atlas_client.words_to_segments(words),
        )


if __name__ == "__main__":
    unittest.main()
