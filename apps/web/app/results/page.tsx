import styles from "./results.module.css";
import FindingCard, { type Finding } from "./FindingCard";

const findings: Finding[] = [
  {
    name: "Hemoglobin",
    value: "10.2 g/dL",
    status: "Low",
  },
  {
    name: "Vitamin D",
    value: "18 ng/mL",
    status: "Low",
  },
  {
    name: "Glucose",
    value: "92 mg/dL",
    status: "Normal",
  },
  {
  name: "Cholesterol",
  value: "210 mg/dL",
  status: "High",
},
];

export default function ResultsPage() {
  return (
    <main>
      <h1>Your Results</h1>

      <section>
        <h2>What does your report mean?</h2>

        <p>
          Your report contains a few results that may need attention.
        </p>
      </section>

      <section>
        <h2>Key Findings</h2>

        <div className={styles.findings}>
  {findings.map((finding) => (
    <FindingCard
      key={finding.name}
      finding={finding}
    />
  ))}
</div>
      </section>

      <section>
        <h2>Recommended Specialist</h2>

        <h3>General Physician</h3>
      </section>
    </main>
  );
}