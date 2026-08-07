"use client";

import { useState } from "react";
import StepList from "./components/StepList";
import ProblemDisplay from "./components/ProblemDisplay";
import StudentCode from "./components/StudentCode";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;

// recognizedLatex holds a single expression (the step's answer), not a full "lhs = rhs"
// equation - matches how the real evaluator pipeline actually checks a step (confirmed via
// backend/test_orchestration.py's own examples), not how the old mock data looked.
const INITIAL_STEPS = [
  { status: "correct", recognizedLatex: "7/12" },
  { status: "incorrect", recognizedLatex: "2/7" },
  { status: "unanswered", recognizedLatex: "" },
];

const SAMPLE_PROBLEMS = [
  "\\frac{1}{3} + \\frac{1}{4} = \\, ?",
  "\\frac{5}{8} - \\frac{1}{4} = \\, ?",
  "2\\frac{1}{2} \\times \\frac{2}{5} = \\, ?",
];

// Matches SAMPLE_PROBLEMS[0] / INITIAL_STEPS[0]'s existing "7/12" assumption - the UI has no
// real problem-selection concept yet (that's #14's frontend wiring, a separate ticket), so
// this is a deliberate, minimal stopgap to make the real check call meaningful.
const CORRECT_ANSWER = "7/12";

export default function Home() {
  const [steps, setSteps] = useState(INITIAL_STEPS);
  const [results, setResults] = useState(null);
  const [checking, setChecking] = useState(false);
  const [checkError, setCheckError] = useState(null);
  // Not yet sent anywhere - #45/#15 will pick this up to populate Attempt.student_id.
  const [studentCode, setStudentCode] = useState("");

  const addStep = () => {
    setSteps((prev) => [...prev, { status: "unanswered", recognizedLatex: "" }]);
    setResults(null);
  };

  const deleteStep = (index) => {
    setSteps((prev) => prev.filter((_, i) => i !== index));
    setResults(null);
  };

  const handleStepChange = (index, recognizedLatex) => {
    setSteps((prev) => prev.map((step, i) => (i === index ? { ...step, recognizedLatex } : step)));
    setResults(null);
  };

  const checkWork = async () => {
    setChecking(true);
    setCheckError(null);
    try {
      const res = await fetch(`${BACKEND_URL}/attempts/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          steps: steps.map((s) => ({ recognized_latex: s.recognizedLatex })),
          correct_answer: CORRECT_ANSWER,
        }),
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.detail || `Check failed (${res.status})`);
      }
      setResults(await res.json());
    } catch (err) {
      setCheckError(err.message || "Check failed");
    } finally {
      setChecking(false);
    }
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

      <StudentCode onChange={setStudentCode} />

      <div className="flex w-full max-w-md flex-col gap-3">
        <h2 className="text-left text-sm font-medium uppercase tracking-wide text-gray-500">
          Sample problems (mock)
        </h2>
        {SAMPLE_PROBLEMS.map((questionText, index) => (
          <ProblemDisplay key={index} questionText={questionText} />
        ))}
      </div>

      <StepList steps={steps} results={results} onDelete={deleteStep} onStepChange={handleStepChange} />
      {checkError && <p className="text-sm text-red-600">{checkError}</p>}
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
          disabled={checking}
          className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-40"
        >
          {checking ? "Checking…" : "Check my working"}
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
