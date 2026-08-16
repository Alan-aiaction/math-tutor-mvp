"use client";

import { useEffect, useState } from "react";
import StepList from "./components/StepList";
import ProblemDisplay from "./components/ProblemDisplay";
import ParentAuth from "./components/ParentAuth";
import ChildPicker from "./components/ChildPicker";
import ActiveChildHeader from "./components/ActiveChildHeader";
import ScratchPad from "./components/ScratchPad";
import { apiFetch } from "./lib/apiFetch";
import { supabase } from "./lib/supabaseClient";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;
const ACTIVE_CHILD_STORAGE_KEY = "mathTutorActiveChild";

const INITIAL_STEPS = [{ status: "unanswered", recognizedLatex: "" }];

const ALL_CORRECT_MESSAGE = "Goed zo! Je hebt de hele som goed opgelost.";

export default function Home() {
  const [steps, setSteps] = useState(INITIAL_STEPS);
  const [results, setResults] = useState(null);
  const [checking, setChecking] = useState(false);
  const [checkError, setCheckError] = useState(null);
  const [saveError, setSaveError] = useState(null);
  const [problem, setProblem] = useState(null);
  const [loadingProblem, setLoadingProblem] = useState(true);
  const [problemError, setProblemError] = useState(null);

  // 3rd MVP: parent session (Supabase Auth) + active child (localStorage - "session
  // persistence: keep last status", same pattern the old StudentCode component used).
  const [session, setSession] = useState(undefined); // undefined = still checking
  const [activeChild, setActiveChild] = useState(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data: listener } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
      if (!newSession) {
        setActiveChild(null);
        window.localStorage.removeItem(ACTIVE_CHILD_STORAGE_KEY);
      }
    });
    const stored = window.localStorage.getItem(ACTIVE_CHILD_STORAGE_KEY);
    if (stored) {
      try {
        setActiveChild(JSON.parse(stored));
      } catch {
        window.localStorage.removeItem(ACTIVE_CHILD_STORAGE_KEY);
      }
    }
    return () => listener.subscription.unsubscribe();
  }, []);

  const selectChild = (child) => {
    setActiveChild(child);
    window.localStorage.setItem(ACTIVE_CHILD_STORAGE_KEY, JSON.stringify(child));
  };

  const switchChild = () => {
    setActiveChild(null);
    window.localStorage.removeItem(ACTIVE_CHILD_STORAGE_KEY);
  };

  const fetchRandomProblem = () => apiFetch(`${BACKEND_URL}/problems/random`);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await fetchRandomProblem();
        if (!cancelled) setProblem(data);
      } catch (err) {
        if (!cancelled) setProblemError(err.message || "Could not load the problem");
      } finally {
        if (!cancelled) setLoadingProblem(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const loadNextProblem = async () => {
    setLoadingProblem(true);
    setProblemError(null);
    setSteps(INITIAL_STEPS);
    setResults(null);
    setCheckError(null);
    setSaveError(null);
    try {
      const data = await fetchRandomProblem();
      setProblem(data);
    } catch (err) {
      setProblemError(err.message || "Could not load the problem");
    } finally {
      setLoadingProblem(false);
    }
  };

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

  const authHeaders = () => ({
    "Content-Type": "application/json",
    Authorization: `Bearer ${session.access_token}`,
  });

  const persistAttempt = async (checkResults) => {
    try {
      await apiFetch(`${BACKEND_URL}/attempts`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
          problem_id: problem.id,
          child_id: activeChild.id,
          status: "completed",
          steps: steps.map((s, i) => ({
            recognized_latex: s.recognizedLatex,
            is_correct: checkResults[i]?.valid ?? false,
          })),
        }),
      });
    } catch (err) {
      setSaveError(err.message || "Could not save this attempt");
    }
  };

  const checkWork = async () => {
    setChecking(true);
    setCheckError(null);
    setSaveError(null);
    try {
      const data = await apiFetch(`${BACKEND_URL}/attempts/check`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
          steps: steps.map((s) => ({ recognized_latex: s.recognizedLatex })),
          correct_answer: problem.correct_answer,
        }),
      });
      setResults(data);
      await persistAttempt(data);
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

  const allStepsCorrect = results && results.length > 0 && results.every((r) => r.valid);

  if (session === undefined) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-8 p-16 text-center font-sans">
        <p className="text-sm text-gray-500">Loading…</p>
      </main>
    );
  }

  if (!session) {
    return (
      <main className="flex min-h-screen flex-col items-center gap-8 p-16 text-center font-sans">
        <div>
          <h1 className="text-3xl font-semibold">Math Tutor MVP</h1>
        </div>
        <ParentAuth onAuthenticated={setSession} />
      </main>
    );
  }

  if (!activeChild) {
    return (
      <main className="flex min-h-screen flex-col items-center gap-8 p-16 text-center font-sans">
        <div>
          <h1 className="text-3xl font-semibold">Math Tutor MVP</h1>
        </div>
        <ChildPicker
          accessToken={session.access_token}
          onChildSelected={selectChild}
          onSignOut={() => setSession(null)}
        />
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center gap-8 p-16 text-center font-sans">
      <ScratchPad side="left" key={`scratch-left-${problem?.id}`} />
      <ScratchPad side="right" key={`scratch-right-${problem?.id}`} />
      <div>
        <h1 className="text-3xl font-semibold">Math Tutor MVP</h1>
        <p className="text-gray-600">Placeholder deployment — real UI coming in Phase 9.</p>
      </div>

      <ActiveChildHeader nickname={activeChild.nickname} onSwitchChild={switchChild} />

      <div className="flex w-full max-w-md flex-col gap-3">
        <h2 className="text-left text-sm font-medium uppercase tracking-wide text-gray-500">
          Problem
        </h2>
        {loadingProblem && <p className="text-sm text-gray-500">Loading problem…</p>}
        {problemError && <p className="text-sm text-red-600">{problemError}</p>}
        {problem && <ProblemDisplay questionText={problem.question_text} />}
      </div>

      <StepList
        steps={steps}
        results={results}
        onDelete={deleteStep}
        onStepChange={handleStepChange}
        problemId={problem?.id}
      />
      {allStepsCorrect && (
        <p className="text-sm font-medium text-emerald-700">{ALL_CORRECT_MESSAGE}</p>
      )}
      {checkError && <p className="text-sm text-red-600">{checkError}</p>}
      {saveError && <p className="text-sm text-amber-600">{saveError}</p>}
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
          disabled={checking || !problem}
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
        <button
          type="button"
          onClick={loadNextProblem}
          disabled={checking || loadingProblem}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40"
        >
          Next problem
        </button>
      </div>
    </main>
  );
}
