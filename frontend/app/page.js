"use client";

import { useState } from "react";
import StepList from "./components/StepList";

const INITIAL_STEPS = [
  { status: "correct" },
  { status: "incorrect" },
  { status: "unanswered" },
];

export default function Home() {
  const [steps, setSteps] = useState(INITIAL_STEPS);

  const addStep = () => {
    setSteps((prev) => [...prev, { status: "unanswered" }]);
  };

  const deleteStep = (index) => {
    setSteps((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <main className="flex min-h-screen flex-col items-center gap-8 p-16 text-center font-sans">
      <div>
        <h1 className="text-3xl font-semibold">Math Tutor MVP</h1>
        <p className="text-gray-600">Placeholder deployment — real UI coming in Phase 9.</p>
      </div>
      <StepList steps={steps} onDelete={deleteStep} />
      <button
        type="button"
        onClick={addStep}
        className="rounded-lg border-2 border-dashed border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:border-gray-400 hover:text-gray-800"
      >
        + Add next step
      </button>
    </main>
  );
}
