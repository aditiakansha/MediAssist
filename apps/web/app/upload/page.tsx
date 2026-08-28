"use client";

import { useState } from "react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  function handleAnalyze() {
  if (!file) return;

  setIsAnalyzing(true);

  setTimeout(() => {
    window.location.href = "/results";
  }, 2000);
}

  function handleFileChange(
  event: React.ChangeEvent<HTMLInputElement>
) {
  const selectedFile = event.target.files?.[0];

  if (!selectedFile) return;

  const allowedTypes = [
    "application/pdf",
    "image/jpeg",
    "image/png",
  ];

  if (!allowedTypes.includes(selectedFile.type)) {
    alert("Please upload a PDF, JPG, or PNG file.");
    return;
  }

  const maxSize = 10 * 1024 * 1024;

if (selectedFile.size > maxSize) {
  alert("File must be smaller than 10 MB.");
  return;
}

  setFile(selectedFile);
}

  return (
    <main>
      <h1>Upload Medical Report</h1>

      <p>
        Upload your report and MediAssist will help you understand it.
      </p>

      <div>
        <p>📄</p>

        <h2>Upload your report</h2>

        <p>Drag & drop your file here</p>

        <p>or</p>

        <label htmlFor="report-upload">
          Browse files
        </label>

        <input
          id="report-upload"
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={handleFileChange}
          hidden
        />

        <p>PDF, JPG or PNG</p>
      </div>

      {file && (
        <div>
          <p>Selected file:</p>
          <strong>{file.name}</strong>

          <button onClick={() => setFile(null)}>
            Remove
          </button>

          <button
  onClick={() => {
    if (file) {
      window.location.href = "/processing";
    }
  }}
  disabled={!file}
>
  Analyze Report
</button>
        </div>
      )}
    </main>
  );
}