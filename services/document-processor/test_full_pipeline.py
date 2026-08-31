"""Test full extraction pipeline: cleaning + artifact detection + medical extraction"""
from app.text_cleaner import clean_extracted_text
from app.medical_extractor import MedicalEntityExtractor

# Realistic medical text from a clinical document
raw_text = """
Case:/g3/g3MD/g88209/g882
Physician:/g3MD

Date: August 8, 2009
Medical Consultant:/g3MD

Patient Demographics:
The patient was a 73 year old female with a history of hypertension, hypothyroidism and depression.

Chief Complaint:
Patient presented with syncope (loss of consciousness) and chest pain.

Physical Examination:
BP 140/90 mmHg, HR 72

Laboratory Results:
Hemoglobin: 13.5 g/dL
Hematocrit: 40%
D-dimer: 0.45 ng/mL
Creatinine: 1.2 mg/dL

Imaging Studies:
CT abdomen showed an abdominal aortic aneurysm measuring 4.9/g8825.0 cm.
CT pulmonary arteries revealed mild atherosclerotic changes.

Cardiac:
Atrial fibrillation noted on EKG. Sick sinus syndrome suspected.

Current Medications:
Warfarin 5 mg daily for atrial fibrillation
Sotalol 80 mg twice daily for rate control
Vytorin 10/40 mg daily for cholesterol
Keflex 500 mg four times daily (antibiotic course)

Assessment:
Abdominal aortic aneurysm with rupture risk. Syncope likely secondary to arrhythmia.
Recommended urgent vascular surgery consultation and cardiology follow-up.
"""

print("=" * 70)
print("MEDIASSIST EXTRACTION PIPELINE TEST")
print("=" * 70)

# Step 1: Clean and detect artifacts
print("\n1. TEXT CLEANING & ARTIFACT DETECTION")
print("-" * 70)
cleaning_result = clean_extracted_text(raw_text)

print(f"Original text length: {len(raw_text)} chars")
print(f"Cleaned text length: {len(cleaning_result.cleaned_text)} chars")
print(f"Artifacts detected: {len(cleaning_result.detected_artifacts)}")
print(f"Contains uncertain data: {cleaning_result.has_uncertain_data}")

if cleaning_result.detected_artifacts:
    print("\nDetected artifacts (requires human review):")
    for artifact in cleaning_result.detected_artifacts:
        print(f"  - '{artifact.location_text}' (line {artifact.line_number})")

# Step 2: Extract medical entities
print("\n2. MEDICAL ENTITY EXTRACTION")
print("-" * 70)
extractor = MedicalEntityExtractor("clinical_report.pdf")
doc = extractor.extract_document(cleaning_result.cleaned_text)

print(f"Patient:")
if doc.patient.age:
    print(f"  Age: {doc.patient.age} years")
if doc.patient.sex:
    print(f"  Sex: {doc.patient.sex}")

print(f"\nMedical History ({len(doc.medical_history)} conditions):")
for condition in doc.medical_history[:5]:
    print(f"  - {condition.name} ({condition.status})")

print(f"\nSymptoms ({len(doc.symptoms)} found):")
for symptom in doc.symptoms[:5]:
    print(f"  - {symptom.description}")

print(f"\nMedications ({len(doc.medications)} found):")
for med in doc.medications[:5]:
    dose_info = f" {med.dose}" if med.dose else ""
    freq_info = f" {med.frequency}" if med.frequency else ""
    print(f"  - {med.name}{dose_info}{freq_info}")

print(f"\nLab Results ({len(doc.lab_results)} found):")
for lab in doc.lab_results[:5]:
    value_info = f": {lab.value}" if lab.value else ""
    unit_info = f" {lab.unit}" if lab.unit else ""
    print(f"  - {lab.test_name}{value_info}{unit_info}")

print(f"\nImaging Findings ({len(doc.imaging_findings)} found):")
for imaging in doc.imaging_findings[:5]:
    print(f"  - {imaging.modality}: {imaging.finding}")

print(f"\n3. DOCUMENT QUALITY METRICS")
print("-" * 70)
print(f"Extraction version: {doc.extraction_version}")
print(f"Extraction quality: {doc.extraction_quality}")
print(f"Contains uncertain data: {doc.contains_uncertain_data}")
print(f"Warnings: {len(doc.warnings)}")

print("\n" + "=" * 70)
print("PIPELINE COMPLETE")
print("=" * 70)
