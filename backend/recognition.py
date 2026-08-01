"""Recognition Service wrapper for MyScript's iink Cloud REST API (task #18).

Sends handwritten ink strokes for batch math recognition and returns the
recognized LaTeX string. See:
https://developer.myscript.com/doc/interactive-ink/3.2/web/rest/architecture/

No confidence score: MyScript's math recognition has no confidence field
(verified against the JIIX schema docs and a live test call) - the team
decided to always show the frontend's Confirm/Edit step (#41) instead of
trying to threshold on one. See #21 on the task board.
"""
import hashlib
import hmac as hmac_lib
import json
import os

import requests

MYSCRIPT_BATCH_URL = "https://cloud.myscript.com/api/v4.0/iink/batch"
REQUEST_TIMEOUT_SECONDS = 10


class RecognitionError(Exception):
    """Raised when the MyScript API call fails (auth, timeout, or bad request)."""


def _compute_hmac(app_key: str, hmac_key: str, body: str) -> str:
    user_key = (app_key + hmac_key).encode("utf-8")
    return hmac_lib.new(user_key, body.encode("utf-8"), hashlib.sha512).hexdigest()


def recognize_math(stroke_groups: list, width: int, height: int) -> str:
    """Recognize handwritten math ink and return the recognized LaTeX string.

    Raises RecognitionError on timeout, auth failure, or any non-200 response,
    instead of letting the request crash the caller.
    """
    app_key = os.environ.get("MYSCRIPT_APP_KEY")
    hmac_key = os.environ.get("MYSCRIPT_HMAC_KEY")
    if not app_key or not hmac_key:
        raise RecognitionError("MyScript credentials are not configured")

    payload = {
        "configuration": {
            "math": {
                "mimeTypes": ["application/x-latex"],
                "solver": {"enable": True},
            },
            "lang": "en_US",
        },
        "xDPI": 96,
        "yDPI": 96,
        "contentType": "Math",
        "strokeGroups": stroke_groups,
        "width": width,
        "height": height,
    }
    body = json.dumps(payload)

    headers = {
        # Accept controls which single format comes back - "application/x-latex"
        # returns the raw LaTeX string as the response body, verified live.
        "Accept": "application/x-latex",
        "Content-Type": "application/json",
        "applicationKey": app_key,
        "hmac": _compute_hmac(app_key, hmac_key, body),
    }

    try:
        response = requests.post(
            MYSCRIPT_BATCH_URL, data=body, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
        )
    except requests.exceptions.RequestException as exc:
        raise RecognitionError(f"MyScript request failed: {exc}") from exc

    if response.status_code != 200:
        raise RecognitionError(
            f"MyScript API returned {response.status_code}: {response.text[:300]}"
        )

    return response.text
