"""
Text cleaning and PDF artifact detection for MediAssist.

This module handles both cleaning of extracted text and detection of uncertain
PDF artifacts. It preserves uncertainty rather than guessing at medical values.

Key principle: For medical data, it's better to flag uncertainty than to
fabricate values. For example, "/g8825" might be many things - we detect it
and flag it rather than guessing it's a specific character.
"""

import re
from typing import NamedTuple

from app.schemas import ExtractionArtifact


class CleaningResult(NamedTuple):
    """Result from text cleaning and artifact detection."""

    cleaned_text: str
    detected_artifacts: list[ExtractionArtifact]
    has_uncertain_data: bool


# Known PDF encoding artifacts that we can safely clean
SAFE_ARTIFACTS = {
    "/g3": " ",  # Common spacing artifact
    "/g882": " ",  # Space-like artifact
}

# Known suspicious artifacts we should detect but NOT replace
# These appear in medical text and their meaning is unclear
SUSPICIOUS_PATTERNS = [
    (r"/g\d{3,5}", "PDF encoding artifact"),  # /g followed by 3-5 digits
    (r"[^\x20-\x7E\n\t]", "Non-ASCII character"),  # Non-printable characters
]


def clean_extracted_text(text: str) -> CleaningResult:
    """
    Clean and validate extracted PDF text, detecting suspicious artifacts.

    This function:
    1. Detects suspicious PDF encoding artifacts
    2. Applies safe cleaning operations
    3. Returns both cleaned text and detected artifacts
    4. Sets has_uncertain_data flag if artifacts found

    Args:
        text: Raw extracted text from PDF

    Returns:
        CleaningResult with cleaned_text, detected_artifacts, and has_uncertain_data flag

    Safety principle: Never guess at medical values. If something is uncertain,
    flag it for human review rather than inventing a replacement.
    """

    if not text:
        return CleaningResult(
            cleaned_text="",
            detected_artifacts=[],
            has_uncertain_data=False,
        )

    detected_artifacts: list[ExtractionArtifact] = []
    working_text = text

    # Scan for suspicious patterns BEFORE cleaning
    line_number = 0
    for line in working_text.split("\n"):
        line_number += 1
        for pattern, artifact_type in SUSPICIOUS_PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                artifact = ExtractionArtifact(
                    artifact_type=artifact_type,
                    location_text=match.group(),
                    suspected_meaning=None,  # Unknown - preserve uncertainty
                    line_number=line_number,
                    confidence=0.0,  # No confidence in interpretation
                )
                detected_artifacts.append(artifact)

    # Apply only SAFE cleaning operations
    for artifact_text, replacement in SAFE_ARTIFACTS.items():
        working_text = working_text.replace(artifact_text, replacement)

    # Normalize non-breaking spaces (safe)
    working_text = working_text.replace("\u00a0", " ")

    # Normalize different dash characters to standard hyphen (safe)
    working_text = re.sub(r"[‐-‒–—]", "-", working_text)

    # Collapse repeated whitespace while preserving paragraphs (safe)
    working_text = re.sub(r"[ \t]+", " ", working_text)

    # Remove spaces immediately before punctuation (safe)
    working_text = re.sub(r"\s+([,.;:!?])", r"\1", working_text)

    # Normalize excessive blank lines (safe)
    working_text = re.sub(r"\n\s*\n\s*\n+", "\n\n", working_text)

    cleaned_text = working_text.strip()

    # Flag if we found suspicious data
    has_uncertain_data = len(detected_artifacts) > 0

    return CleaningResult(
        cleaned_text=cleaned_text,
        detected_artifacts=detected_artifacts,
        has_uncertain_data=has_uncertain_data,
    )