"""External AI integration (Google Gemini REST API)."""
import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


class AIServiceError(Exception):
    pass


def _age(dob):
    born = datetime.strptime(dob, "%d/%m/%Y").date()
    today = datetime.today().date()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def predict_health_risk(patient):
    """Return a short, plain-text risk remark for validated patient data."""
    if not API_KEY:
        raise AIServiceError("GEMINI_API_KEY is not set (see .env.example).")

    prompt = (
        "You are a clinical decision-support assistant. Based on these blood test results, "
        "state the most likely health condition or disease risk (e.g. diabetes, anaemia, "
        "high cholesterol / cardiovascular risk, or 'no significant risk'). "
        "Reply in at most 2 short sentences, plain text, and add 'Consult a doctor.' at the end.\n"
        f"Age: {_age(patient['dob'])} years\n"
        f"Glucose: {patient['glucose']} mg/dL\n"
        f"Haemoglobin: {patient['haemoglobin']} g/dL\n"
        f"Cholesterol: {patient['cholesterol']} mg/dL"
    )
    try:
        for attempt in range(4):
            resp = requests.post(
                URL,
                headers={"x-goog-api-key": API_KEY, "Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30,
            )
            # Retry on rate-limit / temporary server errors
            if resp.status_code in (429, 500, 503) and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            break
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except requests.RequestException as exc:
        raise AIServiceError(f"AI API request failed: {exc}")
    except (KeyError, IndexError, ValueError):
        raise AIServiceError("AI API returned an unexpected response.")
