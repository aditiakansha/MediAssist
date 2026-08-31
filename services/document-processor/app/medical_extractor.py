"""
Medical entity extraction from clinical documents.

This module extracts structured medical entities from cleaned text using
pattern matching and keyword recognition. This provides a foundation that
can later be enhanced with LLM-based extraction for more complex cases.

Current approach:
- Pattern-based extraction for structured data (age, dates, test values)
- Keyword-based extraction for conditions, medications, procedures
- Conservative confidence scoring based on pattern match quality
- Source text references for validation
"""

import re
from datetime import datetime

from app.schemas import (
    ClinicalEvent,
    ImagingFinding,
    LabResult,
    MedicalCondition,
    MedicalDocument,
    Medication,
    PatientDemographics,
)


class MedicalEntityExtractor:
    """Extract medical entities from clinical document text."""

    def __init__(self, filename: str):
        """
        Initialize extractor for a document.

        Args:
            filename: Name of the source document
        """
        self.filename = filename

    def extract_patient_demographics(self, text: str) -> PatientDemographics:
        """Extract patient demographics (age, sex, etc.)."""
        demographics = PatientDemographics()

        # Extract age: look for "age" or "yo" (year old)
        age_patterns = [
            r"(?:age|aged?|yr|years old)[\s:]*(\d{1,3})",
            r"(\d{1,3})[\s-](?:year|yr)[\s-]old",
            r"(\d{1,3})[\s-]y\.o\.",
        ]

        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    age = int(match.group(1))
                    if 0 <= age <= 150:
                        demographics.age = age
                        break
                except (ValueError, IndexError):
                    continue

        # Extract sex: look for male/female/M/F
        sex_patterns = [
            (r"\bmale\b", "male"),
            (r"\bfemale\b", "female"),
            (r"\b([mM])\b(?:\s|$)", "male"),
            (r"\b([fF])\b(?:\s|$)", "female"),
        ]

        for pattern, sex_value in sex_patterns:
            if re.search(pattern, text):
                demographics.sex = sex_value
                break

        return demographics

    def extract_medical_conditions(self, text: str) -> list[MedicalCondition]:
        """Extract medical conditions and diagnoses."""
        conditions = []

        # Common medical condition keywords
        condition_keywords = [
            "hypertension",
            "hypotension",
            "diabetes",
            "hypothyroidism",
            "hyperthyroidism",
            "depression",
            "anxiety",
            "syncope",
            "arrhythmia",
            "atrial fibrillation",
            "heart disease",
            "coronary artery disease",
            "heart failure",
            "myocardial infarction",
            "stroke",
            "transient ischemic attack",
            "pneumonia",
            "asthma",
            "COPD",
            "chronic obstructive pulmonary disease",
            "aneurysm",
            "aortic aneurysm",
            "abdominal aortic aneurysm",
            "thoracic aortic aneurysm",
            "cancer",
            "malignancy",
            "tumor",
            "arthritis",
            "osteoarthritis",
            "rheumatoid arthritis",
            "kidney disease",
            "renal failure",
            "liver disease",
            "cirrhosis",
            "hepatitis",
            "ulcer",
            "gastroesophageal reflux",
            "GERD",
            "hyperlipidemia",
            "high cholesterol",
            "obesity",
            "anemia",
            "bleeding disorder",
            "coagulation disorder",
            "thrombosis",
            "pulmonary embolism",
            "deep vein thrombosis",
        ]

        seen = set()
        for keyword in condition_keywords:
            pattern = rf"\b{re.escape(keyword)}\b"
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                key = keyword.lower()
                if key not in seen:
                    seen.add(key)
                    condition = MedicalCondition(
                        name=keyword.lower(),
                        status="documented",
                        confidence=0.85,  # Keyword match confidence
                        source_text=match.group(),
                    )
                    conditions.append(condition)

        return conditions

    def extract_medications(self, text: str) -> list[Medication]:
        """Extract medications with dose and frequency info."""
        medications = []

        # Common medication names
        medication_keywords = [
            "warfarin",
            "aspirin",
            "ibuprofen",
            "acetaminophen",
            "metformin",
            "lisinopril",
            "atenolol",
            "metoprolol",
            "amlodipine",
            "amoxicillin",
            "penicillin",
            "erythromycin",
            "azithromycin",
            "fluoroquinolone",
            "cephalosporin",
            "simvastatin",
            "atorvastatin",
            "pravastatin",
            "levothyroxine",
            "synthroid",
            "insulin",
            "furosemide",
            "hydrochlorothiazide",
            "chlorothiazide",
            "spironolactone",
            "amiodarone",
            "digoxin",
            "sotalol",
            "vytorin",
            "keflex",
            "zocor",
            "lipitor",
            "plavix",
            "clopidogrel",
            "ticlopidine",
            "heparin",
            "enoxaparin",
            "lovenox",
            "apixaban",
            "rivaroxaban",
            "dabigatran",
            "warfarin",
        ]

        seen = set()
        for med_name in medication_keywords:
            pattern = rf"\b{re.escape(med_name)}(?:\s+\d+\s*(?:mg|ml|mcg|units?))?(?:\s+(?:tablet|tab|capsule|cap|liquid|oral|iv|im|inj))?\b"
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                key = med_name.lower()
                if key not in seen:
                    seen.add(key)
                    source = match.group().strip()

                    # Try to extract dose
                    dose_match = re.search(r"(\d+\.?\d*)\s*(mg|ml|mcg|g|units?)", source, re.IGNORECASE)
                    dose = f"{dose_match.group(1)} {dose_match.group(2)}" if dose_match else None

                    # Try to extract frequency
                    frequency_patterns = [
                        r"(daily|once daily|b\.?i\.?d|twice daily|t\.i\.?d|three times daily|q\.i\.?d|four times daily)",
                        r"every\s+(\d+)\s+(?:hours?|h)",
                    ]
                    frequency = None
                    for freq_pattern in frequency_patterns:
                        freq_match = re.search(freq_pattern, source, re.IGNORECASE)
                        if freq_match:
                            frequency = freq_match.group().lower()
                            break

                    medication = Medication(
                        name=med_name.lower(),
                        dose=dose,
                        frequency=frequency,
                        confidence=0.8,
                        source_text=source,
                    )
                    medications.append(medication)

        return medications

    def extract_lab_results(self, text: str) -> list[LabResult]:
        """Extract laboratory test results."""
        results = []

        # Common lab test names and their patterns
        lab_tests = {
            "hemoglobin": r"hemoglobin|hgb|hb",
            "hematocrit": r"hematocrit|hct",
            "white blood cell": r"wbc|white blood cell|leukocyte",
            "platelet": r"platelet|plt",
            "red blood cell": r"rbc|red blood cell",
            "d-dimer": r"d-?dimer|d-?dimer",
            "glucose": r"glucose|blood sugar",
            "creatinine": r"creatinine",
            "bun": r"bun|blood urea nitrogen",
            "sodium": r"sodium|na\+",
            "potassium": r"potassium|k\+",
            "chloride": r"chloride|cl-",
            "calcium": r"calcium|ca",
            "magnesium": r"magnesium|mg",
            "phosphorus": r"phosphorus",
            "albumin": r"albumin",
            "bilirubin": r"bilirubin",
            "alt": r"alt|alanine aminotransferase",
            "ast": r"ast|aspartate aminotransferase",
            "ldh": r"ldh|lactate dehydrogenase",
            "cholesterol": r"cholesterol|total cholesterol",
            "hdl": r"hdl|high density lipoprotein",
            "ldl": r"ldl|low density lipoprotein",
            "triglycerides": r"triglyceride",
        }

        for test_name, pattern in lab_tests.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Look for value after test name
                start_pos = match.end()
                value_text = text[start_pos : start_pos + 50]
                value_match = re.search(r"(\d+\.?\d*)\s*([a-z/]+)?", value_text)

                value = None
                unit = None
                if value_match:
                    value = value_match.group(1)
                    unit = value_match.group(2).strip() if value_match.group(2) else None

                result = LabResult(
                    test_name=test_name,
                    value=value,
                    unit=unit,
                    confidence=0.75,
                    source_text=match.group(),
                )
                results.append(result)
                break  # Only extract first match per test name

        return results

    def extract_imaging_findings(self, text: str) -> list[ImagingFinding]:
        """Extract imaging study findings."""
        findings = []

        # Imaging modalities and associated findings
        imaging_modalities = [
            "ct",
            "computed tomography",
            "mri",
            "magnetic resonance",
            "x-ray",
            "xray",
            "ultrasound",
            "echocardiogram",
            "ekg",
            "pet scan",
            "nuclear medicine",
        ]

        imaging_findings_keywords = [
            "aneurysm",
            "atherosclerotic",
            "ectasia",
            "aortic",
            "cardiomegaly",
            "effusion",
            "infiltrate",
            "consolidation",
            "pneumonia",
            "pleural",
            "embolism",
            "thrombosis",
            "infarction",
            "stroke",
            "hemorrhage",
            "mass",
            "lesion",
            "fracture",
            "dislocation",
        ]

        for modality in imaging_modalities:
            pattern = rf"{re.escape(modality)}.*?(?:\n\n|$)"
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)

            for match in matches:
                study_text = match.group().strip()
                # Look for findings keywords in this study
                for finding_keyword in imaging_findings_keywords:
                    if re.search(rf"\b{finding_keyword}\b", study_text, re.IGNORECASE):
                        finding = ImagingFinding(
                            modality=modality.lower(),
                            finding=finding_keyword,
                            confidence=0.75,
                            source_text=study_text[:100],
                        )
                        findings.append(finding)
                        break

        return findings

    def extract_clinical_events(self, text: str) -> list[ClinicalEvent]:
        """Extract clinical events from document."""
        events = []

        # Common symptom/event keywords
        symptom_keywords = [
            "syncope",
            "fainting",
            "dizziness",
            "chest pain",
            "dyspnea",
            "shortness of breath",
            "fever",
            "cough",
            "hemoptysis",
            "abdominal pain",
            "nausea",
            "vomiting",
            "diarrhea",
            "constipation",
            "headache",
            "weakness",
            "fatigue",
            "palpitations",
            "edema",
            "jaundice",
            "rash",
            "bleeding",
            "hemorrhage",
        ]

        seen = set()
        for symptom in symptom_keywords:
            pattern = rf"\b{re.escape(symptom)}\b"
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                key = symptom.lower()
                if key not in seen:
                    seen.add(key)
                    event = ClinicalEvent(
                        event_type="symptom",
                        description=symptom.lower(),
                        confidence=0.8,
                        source_text=match.group(),
                    )
                    events.append(event)

        return events

    def extract_document(self, text: str) -> MedicalDocument:
        """
        Extract all medical entities from document text.

        Args:
            text: Cleaned document text

        Returns:
            MedicalDocument with all extracted entities
        """
        patient = self.extract_patient_demographics(text)
        medical_history = self.extract_medical_conditions(text)
        medications = self.extract_medications(text)
        lab_results = self.extract_lab_results(text)
        imaging_findings = self.extract_imaging_findings(text)
        symptoms = self.extract_clinical_events(text)

        # Separate diagnoses from history (simplified approach)
        diagnoses = medical_history[:5] if len(medical_history) > 5 else medical_history

        document = MedicalDocument(
            source_filename=self.filename,
            extraction_timestamp=datetime.utcnow(),
            extraction_version="0.1.0",
            patient=patient,
            medical_history=medical_history,
            medications=medications,
            lab_results=lab_results,
            imaging_findings=imaging_findings,
            symptoms=symptoms,
            diagnoses=diagnoses,
            extraction_quality="fair",  # Default to conservative quality
            contains_uncertain_data=False,
            warnings=[],
        )

        return document
