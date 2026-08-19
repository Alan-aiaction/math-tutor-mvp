"use client";

import { useEffect, useState } from "react";
import StepList from "./components/StepList";
import ProblemDisplay from "./components/ProblemDisplay";
import ParentAuth from "./components/ParentAuth";
import ChildPicker from "./components/ChildPicker";
import AppShell from "./components/AppShell";
import ScratchPad from "./components/ScratchPad";
import { apiFetch } from "./lib/apiFetch";
import { supabase } from "./lib/supabaseClient";
import { useLanguage } from "./lib/LanguageContext";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;
const ACTIVE_CHILD_STORAGE_KEY = "mathTutorActiveChild";

const INITIAL_STEPS = [{ status: "unanswered", recognizedLatex: "" }];

const INITIAL_WRONG_TRY_COUNTS = [0];

export default function Home() {
  const { t } = useLanguage();
  const [view, setView] = useState("kinderen"); // "oefenen" | "dashboard" | "kinderen" | "account"
  const [steps, setSteps] = useState(INITIAL_STEPS);
  // wrongTryCounts (ticket #71): how many times each step has already come back
  // wrong in this problem-solving session - parallel to `steps`, sent to the
  // backend so it can trigger hint escalation on a 2nd+ wrong try at the same
  // step. Deliberately NOT reset by handleStepChange - editing a step IS the
  // retry itself, so the count must survive across edits, only resetting when
  // the session itself ends (next problem / clear).
  const [wrongTryCounts, setWrongTryCounts] = useState(INITIAL_WRONG_TRY_COUNTS);
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
        setView("oefenen");
      } catch {
        window.localStorage.removeItem(ACTIVE_CHILD_STORAGE_KEY);
      }
    }
    return () => listener.subscription.unsubscribe();
  }, []);

  // Picking a child from "Mijn kinderen" (or restoring one from localStorage above)
  // both funnel through here - selecting a child now also navigates straight into
  // Oefenen, since that's the reason a parent picks a child in the first place.
  const selectChild = (child) => {
    setActiveChild(child);
    window.localStorage.setItem(ACTIVE_CHILD_STORAGE_KEY, JSON.stringify(child));
    setView("oefenen");
  };

  const handleSignOut = () => {
    supabase.auth.signOut().then(() => setSession(null));
  };

  // Oefenen is only ever reachable with an active child (AppShell already hides the nav
  // item), but if activeChild disappears while still viewing it - e.g. removed from
  // "Mijn kinderen" mid-session - fall back to Dashboard rather than a blank pane.
  useEffect(() => {
    if (view === "oefenen" && !activeChild) setView("dashboard");
  }, [view, activeChild]);

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
    setWrongTryCounts(INITIAL_WRONG_TRY_COUNTS);
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
    setWrongTryCounts((prev) => [...prev, 0]);
    setResults(null);
  };

  const deleteStep = (index) => {
    setSteps((prev) => prev.filter((_, i) => i !== index));
    setWrongTryCounts((prev) => prev.filter((_, i) => i !== index));
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
            // Same value just sent to /attempts/check for this step (KPI data layer) -
            // previously computed and used for hint escalation, then discarded; now
            // also persisted so retry-rate KPIs are computable later.
            previous_wrong_count: wrongTryCounts[i] ?? 0,
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
          steps: steps.map((s, i) => ({
            recognized_latex: s.recognizedLatex,
            previous_wrong_count: wrongTryCounts[i] ?? 0,
          })),
          correct_answer: problem.correct_answer,
          question_text: problem.question_text,
        }),
      });
      setResults(data);
      setWrongTryCounts((prev) => steps.map((_, i) => (data[i]?.valid ? 0 : (prev[i] ?? 0) + 1)));
      await persistAttempt(data);
    } catch (err) {
      setCheckError(err.message || "Check failed");
    } finally {
      setChecking(false);
    }
  };

  const clearSteps = () => {
    setSteps([]);
    setWrongTryCounts([]);
    setResults(null);
  };

  const allStepsCorrect = results && results.length > 0 && results.every((r) => r.valid);

  if (session === undefined) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-8 p-16 text-center">
        <p className="text-sm text-ink-muted">{t("dashboard.loading")}</p>
      </main>
    );
  }

  if (!session) {
    return (
      <main className="flex min-h-screen flex-col items-center gap-8 p-16 text-center">
        <div>
          <h1 className="font-display text-3xl font-bold text-ink">Math Tutor MVP</h1>
        </div>
        <ParentAuth onAuthenticated={setSession} />
      </main>
    );
  }

  return (
    <AppShell activeChild={activeChild} view={view} onNavigate={setView} onSignOut={handleSignOut}>
      {view === "oefenen" && activeChild && (
        <div className="flex flex-col items-center gap-8 text-center">
          <ScratchPad side="left" key={`scratch-left-${problem?.id}`} />
          <ScratchPad side="right" key={`scratch-right-${problem?.id}`} />

          <div className="flex w-full max-w-md flex-col gap-3">
            <h2 className="text-left text-xs font-bold uppercase tracking-wide text-ink-muted">
              {t("oefenen.problemLabel")}
            </h2>
            {loadingProblem && <p className="text-sm text-ink-muted">{t("dashboard.loading")}</p>}
            {problemError && <p className="text-sm text-warn">{problemError}</p>}
            {problem && <ProblemDisplay questionText={problem.question_text} />}
          </div>

          <StepList
            steps={steps}
            results={results}
            onDelete={deleteStep}
            onStepChange={handleStepChange}
            problemId={problem?.id}
          />
          {allStepsCorrect && <p className="text-sm font-bold text-good">{t("oefenen.allCorrect")}</p>}
          {checkError && <p className="text-sm text-warn">{checkError}</p>}
          {saveError && <p className="text-sm text-warm">{saveError}</p>}
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={addStep}
              className="rounded-xl border-2 border-dashed border-border px-4 py-2 text-sm font-bold text-ink-muted hover:border-placeholder-border hover:text-ink"
            >
              {t("oefenen.addStep")}
            </button>
            <button
              type="button"
              onClick={checkWork}
              disabled={checking || !problem}
              className="rounded-xl bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-strong disabled:opacity-40"
            >
              {checking ? t("oefenen.checking") : t("oefenen.check")}
            </button>
            <button
              type="button"
              onClick={clearSteps}
              className="rounded-xl border border-border px-4 py-2 text-sm font-bold text-ink-muted hover:bg-surface"
            >
              {t("oefenen.clear")}
            </button>
            <button
              type="button"
              onClick={loadNextProblem}
              disabled={checking || loadingProblem}
              className="rounded-xl border border-border px-4 py-2 text-sm font-bold text-ink-muted hover:bg-surface disabled:opacity-40"
            >
              {t("oefenen.next")}
            </button>
          </div>
        </div>
      )}

      {view === "kinderen" && (
        <ChildPicker accessToken={session.access_token} onChildSelected={selectChild} />
      )}

      {/* Dashboard/Account real screens land in PR 3 - placeholders keep every nav
          destination reachable and testable now rather than dead-ending. */}
      {view === "dashboard" && <p className="text-sm text-ink-muted">{t("nav.dashboard")} …</p>}
      {view === "account" && <p className="text-sm text-ink-muted">{t("nav.account")} …</p>}
    </AppShell>
  );
}
