"use client";

import { useState } from "react";
import { supabase } from "../lib/supabaseClient";

// 3rd MVP: parent sign up / sign in, one screen, toggled. Goes straight to Supabase Auth
// (never through the backend) - the anon key + client SDK are exactly what this is for.
// onAuthenticated fires with the resulting session once sign-in/sign-up succeeds; the
// parent's ongoing session itself is tracked by supabase.auth.onAuthStateChange in the
// parent component (page.js), not here.
export default function ParentAuth({ onAuthenticated }) {
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
      const { data, error: authError } = isSignUp
        ? await supabase.auth.signUp({ email, password })
        : await supabase.auth.signInWithPassword({ email, password });
      if (authError) {
        setError(authError.message);
        return;
      }
      onAuthenticated?.(data.session);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex w-full max-w-md flex-col gap-3">
      <h2 className="text-left text-sm font-medium uppercase tracking-wide text-gray-500">
        {isSignUp ? "Create your account" : "Sign in"}
      </h2>
      <form onSubmit={submit} className="flex flex-col gap-3">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
          minLength={6}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-40"
        >
          {loading ? "Please wait…" : isSignUp ? "Sign up" : "Sign in"}
        </button>
      </form>
      <button
        type="button"
        onClick={() => {
          setMode(isSignUp ? "signin" : "signup");
          setError(null);
        }}
        className="text-xs font-medium text-blue-600 hover:underline"
      >
        {isSignUp ? "Already have an account? Sign in" : "New here? Sign up"}
      </button>
    </div>
  );
}
