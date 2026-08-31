"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function ProcessingPage() {
  const router = useRouter();

  useEffect(() => {
    const timer = setTimeout(() => {
      router.push("/results");
    }, 3000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <main>
      <h1>Analyzing your report...</h1>

      <p>Please wait while MediAssist processes your report.</p>

      <p>Reading report...</p>
      <p>Extracting information...</p>
      <p>Preparing your results...</p>
    </main>
  );
}