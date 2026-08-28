import Link from "next/link";

export default function Home() {
  return (
    <main>
      <h1>MediAssist</h1>

      <p>
        Understand your medical reports in simple, patient-friendly language.
      </p>

      <Link href="/upload">
        Upload Report
      </Link>

      <Link href="/prescription">
        Analyze Prescription
      </Link>
    </main>
  );
}