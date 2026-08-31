from pathlib import Path
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.pdf_extractor import extract_text_from_pdf
from app.text_cleaner import clean_extracted_text
from app.medical_extractor import MedicalEntityExtractor


app = FastAPI(
    title="MediAssist Document Processor",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "document-processor",
    }


@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    """
    Extract and process a medical PDF document.

    Returns:
        MedicalDocument schema with:
        - Cleaned text
        - Detected PDF artifacts
        - Extracted medical entities (demographics, conditions, medications, etc)
        - Quality metrics and uncertainty flags
    """
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        # Step 1: Extract raw text from PDF
        raw_text = extract_text_from_pdf(temp_path)

        # Step 2: Clean text and detect artifacts
        cleaning_result = clean_extracted_text(raw_text)

        # Step 3: Extract medical entities
        extractor = MedicalEntityExtractor(file.filename)
        medical_doc = extractor.extract_document(cleaning_result.cleaned_text)

        # Step 4: Add detected artifacts to the document
        medical_doc.detected_artifacts = cleaning_result.detected_artifacts
        medical_doc.contains_uncertain_data = cleaning_result.has_uncertain_data

        # Step 5: Update quality assessment
        if cleaning_result.has_uncertain_data:
            medical_doc.extraction_quality = "fair"
            medical_doc.warnings.append(
                f"Found {len(cleaning_result.detected_artifacts)} PDF artifacts requiring review"
            )
        else:
            medical_doc.extraction_quality = "good"

        return medical_doc

    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)