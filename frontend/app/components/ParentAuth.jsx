"use client";

import { useState } from "react";
import { supabase } from "../lib/supabaseClient";
import { useLanguage } from "../lib/LanguageContext";

// 3rd MVP: parent sign up / sign in, one screen, toggled. Goes straight to Supabase Auth
// (never through the backend) - the anon key + client SDK are exactly what this is for.
// onAuthenticated fires with the resulting session once sign-in/sign-up succeeds; the
// parent's ongoing session itself is tracked by supabase.auth.onAuthStateChange in the
// parent component (page.js), not here.
export default function ParentAuth({ onAuthenticated }) {
  const { t } = useLanguage();
  const [mode, setMode] = useState("signin"); // "signin" | "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const isSignUp = mode === "signup";

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      // emailRedirectTo (bug #76): without it, Supabase falls back to the dashboard's
      // Site URL for the confirmation email's link - window.location.origin adapts to
      // whichever environment sign-up actually happened in, instead of a hardcoded URL
      // that would itself go stale if the domain ever changes.
      const { data, error: authError } = isSignUp
        ? await supabase.auth.signUp({ email, password, options: { emailRedirectTo: window.location.origin } })
        : await supabase.auth.signInWithPassword({ email, password });
      if (authError) {
        setError(authError.message);
        return;
      }
      onAuthenticated?.(data.session);
    } catch (err) {
      setError(err.message || t("parentAuth.genericError"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex w-full max-w-md flex-col gap-3">
      <h2 className="text-left text-sm font-bold uppercase tracking-wide text-ink-muted">
        {isSignUp ? t("parentAuth.createAccount") : t("parentAuth.signIn")}
      </h2>
      <form onSubmit={submit} className="flex flex-col gap-3">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={t("parentAuth.email")}
          required
          className="rounded-xl border border-border px-3 py-2 text-sm"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={t("parentAuth.password")}
          required
          minLength={6}
          className="rounded-xl border border-border px-3 py-2 text-sm"
        />
        {error && <p className="text-sm text-warn">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="rounded-xl bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-strong disabled:opacity-40"
        >
          {loading ? t("parentAuth.pleaseWait") : isSignUp ? t("parentAuth.signUp") : t("parentAuth.signIn")}
        </button>
        {isSignUp && (
          <p className="text-xs text-ink-muted">
            {t("parentAuth.privacyNoticePrefix")}{" "}
            <a href="/privacy" target="_blank" rel="noopener noreferrer" className="underline hover:text-ink">
              {t("privacy.linkLabel")}
            </a>
            .
          </p>
        )}
      </form>
      <button
        type="button"
        onClick={() => {
          setMode(isSignUp ? "signin" : "signup");
          setError(null);
        }}
        className="text-xs font-bold text-primary hover:underline"
      >
        {isSignUp ? t("parentAuth.alreadyHaveAccount") : t("parentAuth.newHere")}
      </button>
    </div>
  );
}
