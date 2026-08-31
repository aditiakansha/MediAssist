"""
Medical data schemas for MediAssist document extraction.

This module defines Pydantic models that structure extracted medical information
from clinical documents. These models serve as the contract between the document
processor and downstream systems (RAG, explanation generation, etc.).

Each model includes:
- Required fields for critical medical data
- Optional fields with defaults for uncertain/missing values
- Confidence scores to track extraction certainty
- Source references to map back to original document text
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PatientDemographics(BaseModel):
    """Patient demographic and personal information."""

    age: Optional[int] = Field(
        None,
        description="Patient age in years",
        ge=0,
        le=150,
    )
    sex: Optional[str] = Field(
        None,
        description="Patient biological sex (male/female/other/unknown)",
    )
    name: Optional[str] = Field(None, description="Patient name if present")
    medical_record_number: Optional[str] = Field(None, description="Medical record ID")
    date_of_birth: Optional[str] = Field(None, description="Patient DOB (ISO 8601 format: YYYY-MM-DD)")

    class Config:
        json_schema_extra = {
            "example": {
                "age": 73,
                "sex": "female",
                "name": None,
                "medical_record_number": None,
                "date_of_birth": None,
            }
        }


class MedicalCondition(BaseModel):
    """A single medical condition or diagnosis."""

    name: str = Field(..., description="Condition/diagnosis name")
    status: Optional[str] = Field(
        "documented",
        description="Status: active/resolved/history/suspected/ruled-out",
    )
    onset_date: Optional[str] = Field(None, description="When condition started (ISO 8601 format: YYYY-MM-DD)")
    confidence: float = Field(
        1.0,
        description="Extraction confidence (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    source_text: Optional[str] = Field(None, description="Original text from document")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "hypertension",
                "status": "active",
                "onset_date": None,
                "confidence": 0.95,
                "source_text": "History of hypertension",
            }
        }


class Medication(BaseModel):
    """A single medication/drug entry."""

    name: str = Field(..., description="Drug/medication name")
    dose: Optional[str] = Field(None, description="Dose amount and unit")
    frequency: Optional[str] = Field(None, description="Frequency of administration")
    route: Optional[str] = Field(None, description="Route (oral/IV/IM/topical/etc)")
    duration: Optional[str] = Field(
        None, description="Duration of therapy (e.g., '7 days', 'ongoing')"
    )
    indication: Optional[str] = Field(None, description="Why this drug is prescribed")
    confidence: float = Field(1.0, description="Extraction confidence", ge=0.0, le=1.0)
    source_text: Optional[str] = Field(None, description="Original text from document")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Warfarin",
                "dose": "5 mg",
                "frequency": "daily",
                "route": "oral",
                "duration": "ongoing",
                "indication": "atrial fibrillation",
                "confidence": 0.95,
                "source_text": "Warfarin 5mg daily",
            }
        }


class LabResult(BaseModel):
    """A single laboratory test result."""

    test_name: str = Field(..., description="Name of lab test")
    value: Optional[str] = Field(None, description="Test result value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    reference_range: Optional[str] = Field(None, description="Normal range")
    abnormal: Optional[bool] = Field(None, description="Is result abnormal?")
    test_date: Optional[str] = Field(None, description="Date test was performed (ISO 8601 format: YYYY-MM-DD)")
    confidence: float = Field(1.0, description="Extraction confidence", ge=0.0, le=1.0)
    source_text: Optional[str] = Field(None, description="Original text from document")

    class Config:
        json_schema_extra = {
            "example": {
                "test_name": "Hemoglobin",
                "value": "13.5",
                "unit": "g/dL",
                "reference_range": "13.5-17.5 g/dL",
                "abnormal": False,
                "test_date": None,
                "confidence": 0.95,
                "source_text": "Hemoglobin 13.5 g/dL",
            }
        }


class ImagingFinding(BaseModel):
    """A single imaging study finding."""

    modality: str = Field(
        ...,
        description="Imaging type (CT/MRI/X-ray/Ultrasound/etc)",
    )
    finding: str = Field(..., description="The finding or observation")
    location: Optional[str] = Field(None, description="Anatomical location")
    severity: Optional[str] = Field(
        None,
        description="Severity (mild/moderate/severe) if mentioned",
    )
    study_date: Optional[str] = Field(None, description="Date imaging was performed (ISO 8601 format: YYYY-MM-DD)")
    confidence: float = Field(1.0, description="Extraction confidence", ge=0.0, le=1.0)
    source_text: Optional[str] = Field(None, description="Original text from document")

    class Config:
        json_schema_extra = {
            "example": {
                "modality": "CT abdomen",
                "finding": "Abdominal aortic aneurysm",
                "location": "abdominal aorta",
                "severity": None,
                "study_date": None,
                "confidence": 0.95,
                "source_text": "CT abdomen showed AAA",
            }
        }


class ClinicalEvent(BaseModel):
    """A significant clinical event or finding."""

    event_type: str = Field(
        ...,
        description="Event type: symptom/finding/procedure/hospitalization/etc",
    )
    description: str = Field(..., description="Event description")
    date: Optional[str] = Field(None, description="When event occurred (ISO 8601 format: YYYY-MM-DD)")
    outcome: Optional[str] = Field(None, description="Outcome if mentioned")
    confidence: float = Field(1.0, description="Extraction confidence", ge=0.0, le=1.0)
    source_text: Optional[str] = Field(None, description="Original text from document")

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "symptom",
                "description": "Syncope (loss of consciousness)",
                "date": None,
                "outcome": None,
                "confidence": 0.9,
                "source_text": "Patient presented with syncope",
            }
        }


class ExtractionArtifact(BaseModel):
    """A detected PDF artifact or uncertain extraction."""

    artifact_type: str = Field(
        ...,
        description="Type: encoding_error/suspicious_pattern/unclear_formatting/etc",
    )
    location_text: str = Field(..., description="The problematic text snippet")
    suspected_meaning: Optional[str] = Field(
        None,
        description="What this might represent (uncertain)",
    )
    line_number: Optional[int] = Field(None, description="Approximate line in document")
    confidence: float = Field(
        0.0,
        description="Confidence in extraction (usually low for artifacts)",
        ge=0.0,
        le=1.0,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "artifact_type": "encoding_error",
                "location_text": "/g8825",
                "suspected_meaning": "Unknown - possibly a dash or symbol",
                "line_number": None,
                "confidence": 0.0,
            }
        }


class MedicalDocument(BaseModel):
    """
    Complete extracted and structured medical document.

    This is the primary output schema from the document processor.
    It represents all extracted medical information with confidence scores
    and source references for validation.
    """

    # Document metadata
    source_filename: str = Field(..., description="Original filename")
    extraction_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When extraction occurred",
    )
    extraction_version: str = Field("0.1.0", description="Extraction pipeline version")

    # Patient info
    patient: PatientDemographics = Field(..., description="Patient demographics")

    # Medical history
    medical_history: list[MedicalCondition] = Field(
        default_factory=list,
        description="List of documented medical conditions/diagnoses",
    )

    # Current symptoms and complaints
    symptoms: list[ClinicalEvent] = Field(
        default_factory=list,
        description="Current symptoms and chief complaints",
    )

    # Laboratory results
    lab_results: list[LabResult] = Field(
        default_factory=list,
        description="Laboratory test results",
    )

    # Imaging findings
    imaging_findings: list[ImagingFinding] = Field(
        default_factory=list,
        description="Imaging study findings",
    )

    # Diagnoses/Assessments
    diagnoses: list[MedicalCondition] = Field(
        default_factory=list,
        description="Current diagnoses and assessments",
    )

    # Medications
    medications: list[Medication] = Field(
        default_factory=list,
        description="Current and recent medications",
    )

    # Procedures and interventions
    procedures: list[ClinicalEvent] = Field(
        default_factory=list,
        description="Procedures, surgeries, and interventions",
    )

    # Clinical timeline
    clinical_events: list[ClinicalEvent] = Field(
        default_factory=list,
        description="Chronological clinical events and outcomes",
    )

    # Detected issues
    detected_artifacts: list[ExtractionArtifact] = Field(
        default_factory=list,
        description="PDF artifacts and uncertain extractions (for review)",
    )

    # Overall document metrics
    extraction_quality: str = Field(
        "unknown",
        description="Overall quality: excellent/good/fair/poor",
    )
    contains_uncertain_data: bool = Field(
        False,
        description="Whether document contains artifacts or low-confidence extractions",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Extraction warnings or issues",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "source_filename": "OMC Report Sample - Cardio.pdf",
                "extraction_timestamp": "2026-08-31T12:00:00",
                "extraction_version": "0.1.0",
                "patient": {
                    "age": 73,
                    "sex": "female",
                    "name": None,
                    "medical_record_number": None,
                    "date_of_birth": None,
                },
                "medical_history": [
                    {
                        "name": "hypertension",
                        "status": "active",
                        "confidence": 0.95,
                    },
                    {
                        "name": "hypothyroidism",
                        "status": "active",
                        "confidence": 0.95,
                    },
                ],
                "symptoms": [],
                "lab_results": [],
                "imaging_findings": [],
                "diagnoses": [],
                "medications": [],
                "procedures": [],
                "clinical_events": [],
                "detected_artifacts": [],
                "extraction_quality": "good",
                "contains_uncertain_data": False,
                "warnings": [],
            }
        }
