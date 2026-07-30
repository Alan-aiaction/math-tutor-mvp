"use client";

import { useState } from "react";
import StepList from "./components/StepList";
import { mockCheckWork } from "./lib/mockCheck";

const INITIAL_STEPS = [
  { status: "correct", recognizedLatex: "1/3 + 1/4 = 7/12" },
  { status: "incorrect", recognizedLatex: "1/3 + 1/4 = 2/7" },
  { status: "unanswered", recognizedLatex: "" },
];

export default function Home() {
  const [steps, setSteps] = useState(INITIAL_STEPS);
  const [results, setResults] = useState(null);

  const addStep = () => {
    setSteps((prev) => [...prev, { status: "unanswered", recognizedLatex: "" }]);
    setResults(null);
  };

  const deleteStep = (index) => {
    setSteps((prev) => prev.filter((_, i) => i !== index));
    setResults(null);
  };

  const checkWork = () => {
    setResults(mockCheckWork(steps));
  };

  const clearSteps = () => {
    setSteps([]);
    setResults(null);
  };

  return (
    <main className="flex min-h-screen flex-col items-center gap-8 p-16 text-center font-sans">
      <div>
        <h1 className="text-3xl font-semibold">Math Tutor MVP</h1>
        <p className="text-gray-600">Placeholder deployment — real UI coming in Phase 9.</p>
      </div>
      <StepList steps={steps} results={results} onDelete={deleteStep} />
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={addStep}
          className="rounded-lg border-2 border-dashed border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:border-gray-400 hover:text-gray-800"
        >
          + Add next step
        </button>
        <button
          type="button"
          onClick={checkWork}
          className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800"
        >
          Check my working
        </button>
        <button
          type="button"
          onClick={clearSteps}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50"
        >
          Clear
        </button>
      </div>
    </main>
  );
}
