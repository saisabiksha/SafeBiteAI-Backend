"""Gemini vision food label extraction service.

Extracts visible ingredient text from food packaging images using the Gemini vision model.
Validates structured output before passing extracted terms to the allergen matcher.

Design & Safety Constraints:
- Non-inferential: Instructs the model to only transcribe visible text, never hallucinating or guessing.
- Structured response: Requests and validates JSON with extracted_ingredients, is_complete_and_readable,
  and uncertainty_or_notes.
- Error resilience: Catches API errors, malformed JSON, and network timeouts safely.
- Security: Never prints, logs, or returns the GEMINI_API_KEY.
"""
import json
import logging
from typing import List, Optional, Tuple

from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Supported Gemini vision model
GEMINI_VISION_MODEL = "gemini-2.5-flash"

LABEL_PROMPT = (
    "You are a food label ingredient extractor for SafeBiteAI.\n"
    "Carefully inspect the provided image of a food package or ingredient list.\n"
    "Your objective is to extract ONLY the ingredient text clearly printed on the packaging.\n\n"
    "STRICT RULES:\n"
    "1. Extract ONLY visible ingredients explicitly stated on the packaging.\n"
    "2. Do NOT guess, infer, or assume unlisted or obscured ingredients.\n"
    "3. If the image is blurry, truncated, rotated, partially blocked, or illegible, "
    "set 'is_complete_and_readable' to false and explain the issue in 'uncertainty_or_notes'.\n"
    "4. If no ingredients list is visible in the image, set 'extracted_ingredients' to [] "
    "and 'is_complete_and_readable' to false.\n\n"
    "Return a valid JSON object matching this structure:\n"
    "{\n"
    '  "extracted_ingredients": ["ingredient 1", "ingredient 2"],\n'
    '  "is_complete_and_readable": true,\n'
    '  "uncertainty_or_notes": null\n'
    "}"
)


def extract_ingredients_from_image(
    image_bytes: bytes,
    mime_type: str,
) -> Tuple[List[str], bool, Optional[str]]:
    """
    Sends food label image bytes to Gemini to extract ingredient text.

    Returns:
        Tuple of (extracted_ingredients, is_complete_and_readable, uncertainty_or_notes)
    """
    if not GEMINI_API_KEY:
        return [], False, "Gemini API key is not configured in backend .env."

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_VISION_MODEL,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                LABEL_PROMPT,
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )

        if not response or not response.text:
            return [], False, "No response text received from Gemini vision model."

        data = json.loads(response.text)
        raw_ingredients = data.get("extracted_ingredients", [])
        is_readable = bool(data.get("is_complete_and_readable", False))
        uncertainty = data.get("uncertainty_or_notes")

        if not isinstance(raw_ingredients, list):
            return [], False, "Unexpected response format for ingredients list."

        # Clean individual ingredient strings
        clean_ingredients = [
            str(item).strip()
            for item in raw_ingredients
            if str(item).strip()
        ]

        return clean_ingredients, is_readable, uncertainty

    except Exception as e:
        # Secure error handling: do not log keys or payload details
        error_name = type(e).__name__
        logger.error(f"Gemini label extraction error: {error_name}")
        return [], False, f"Vision extraction failed: {error_name}."
