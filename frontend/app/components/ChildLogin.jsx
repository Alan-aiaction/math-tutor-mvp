"use client";

import { useState } from "react";
import { apiFetch } from "../lib/apiFetch";
import { useLanguage } from "../lib/LanguageContext";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;

// Independent child login (3rd MVP, PR 3 of 3) - a child logs in on their own device
// with no parent session at all, using the family code their parent showed them in
// Account plus their own nickname + password. Calls POST /children/login directly
// (main.py's independent login endpoint, not the parent-mediated child_login_endpoint
// ChildPicker's password gate uses) - success returns {child, token}, which page.js
// stores as the child's own session, separate from the parent's Supabase session.
export default function ChildLogin({ onLoggedIn, onBack }) {
  const { t } = useLanguage();
  const [familyCode, setFamilyCode] = useState("");
  const [nickname, setNickname] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const session = await apiFetch(`${BACKEND_URL}/children/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ family_code: familyCode, nickname, password }),
      });
      onLoggedIn?.(session);
    } catch (err) {
      setError(err.message || t("childLogin.error"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="flex w-full max-w-md flex-col gap-3">
      <h2 className="text-left text-lg font-bold text-ink">{t("childLogin.title")}</h2>
      <input
        type="text"
        value={familyCode}
        onChange={(e) => setFamilyCode(e.target.value)}
        placeholder={t("childLogin.familyCode")}
        required
        className="rounded-xl border border-border px-3 py-2 text-sm"
      />
      <input
        type="text"
        value={nickname}
        onChange={(e) => setNickname(e.target.value)}
        placeholder={t("childpicker.nickname")}
        required
        className="rounded-xl border border-border px-3 py-2 text-sm"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder={t("childpicker.password")}
        required
        className="rounded-xl border border-border px-3 py-2 text-sm"
      />
      {error && <p className="text-sm text-warn">{error}</p>}
      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={submitting}
          className="rounded-xl bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-strong disabled:opacity-40"
        >
          {submitting ? t("parentAuth.pleaseWait") : t("childLogin.submit")}
        </button>
        <button type="button" onClick={onBack} className="text-sm font-bold text-ink-muted hover:underline">
          {t("childLogin.back")}
        </button>
      </div>
    </form>
  );
}
