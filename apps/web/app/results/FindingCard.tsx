import styles from "./FindingCard.module.css";

export type Finding = {
  name: string;
  value: string;
  status: "Normal" | "Low" | "High";
};

type FindingCardProps = {
  finding: Finding;
};

export default function FindingCard({ finding }: FindingCardProps) {
  return (
    <div className={styles.card}>
      <h3 className={styles.name}>
        {finding.name}
      </h3>

      <p className={styles.value}>
        {finding.value}
      </p>

      <span
        className={`${styles.status} ${
          finding.status === "Normal"
            ? styles.normal
            : finding.status === "Low"
              ? styles.low
              : styles.high
        }`}
      >
        {finding.status}
      </span>
    </div>
  );
}