"""Quick test of artifact detection"""
from app.text_cleaner import clean_extracted_text

# Test with artifact
test_text = """The/g3 patient/g3 was/g3 a/g373/g3 year/g3 old
Case:/g3/g3MD/g88209/g882
Result: 4.9/g8825.0cm"""

result = clean_extracted_text(test_text)
print("=== Cleaned Text ===")
print(result.cleaned_text)
print(f"\n=== Detected Artifacts ({len(result.detected_artifacts)}) ===")
for i, artifact in enumerate(result.detected_artifacts, 1):
    print(f"{i}. Type: {artifact.artifact_type}")
    print(f"   Text: {artifact.location_text}")
    print(f"   Line: {artifact.line_number}")
    print(f"   Confidence: {artifact.confidence}")
print(f"\n=== Has Uncertain Data: {result.has_uncertain_data} ===")
