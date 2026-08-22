"use client";

import { useState } from "react";
import { apiFetch } from "../lib/apiFetch";
import { useLanguage } from "../lib/LanguageContext";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;

const CATEGORIES = ["categoryBug", "categoryIdea", "categoryOther"];

// One shared feedback page for both a parent and their child (plan: feedback-page.md) -
// a single 1-5 star rating either role can give, plus a role-appropriate message: a
// parent gets a category picker and a required textarea, a child gets just an optional
// one-line input, since a form is real friction for that age group. authToken is
// whichever bearer token the caller already has (a parent's Supabase access_token or a
// child's own session token) - POST /feedback's require_requester dependency accepts
// either transparently, same as /attempts and /attempts/check.
export default function Feedback({ role, authToken }) {
  const { t } = useLanguage();
  const isParent = role === "parent";
  const [rating, setRating] = useState(0);
  const [category, setCategory] = useState(null);
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [thanks, setThanks] = useState(false);

  const canSubmit = rating > 0 && (!isParent || message.trim() !== "");

  const submit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await apiFetch(`${BACKEND_URL}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${authToken}` },
        body: JSON.stringify({
          rating,
          category: isParent ? category : null,
          message: message.trim() === "" ? null : message.trim(),
        }),
      });
      setRating(0);
      setCategory(null);
      setMessage("");
      setThanks(true);
    } catch (err) {
      setError(err.message || t("feedback.error"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="flex w-full max-w-md flex-col gap-4">
      <h2 className="font-display text-lg font-bold text-ink">{t("feedback.title")}</h2>

      <div className="flex flex-col gap-2 rounded-2xl border border-border bg-bg p-6">
        <span className="text-xs font-bold text-ink-muted">{t("feedback.ratingLabel")}</span>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => {
                setRating(n);
                setThanks(false);
              }}
              aria-label={t("feedback.starAriaLabel", { number: n })}
              aria-pressed={n <= rating}
              className={`text-2xl leading-none ${n <= rating ? "text-primary" : "text-placeholder-border"}`}
            >
              ★
            </button>
          ))}
        </div>
      </div>

      {isParent && (
        <div className="flex gap-2">
          {CATEGORIES.map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => setCategory(t(`feedback.${key}`))}
              aria-pressed={category === t(`feedback.${key}`)}
              className={`rounded-xl border px-3 py-1.5 text-xs font-bold ${
                category === t(`feedback.${key}`) ? "border-primary bg-primary text-white" : "border-border text-ink"
              }`}
            >
              {t(`feedback.${key}`)}
            </button>
          ))}
        </div>
      )}

      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder={t(isParent ? "feedback.messagePlaceholder" : "feedback.messagePlaceholderChild")}
        rows={4}
        className="rounded-xl border border-border px-3 py-2 text-sm"
      />

      {thanks && <p className="text-sm font-bold text-good">{t("feedback.thanks")}</p>}
      {error && <p className="text-sm text-warn">{error}</p>}

      <button
        type="submit"
        disabled={!canSubmit || submitting}
        className="rounded-xl bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-strong disabled:opacity-40"
      >
        {submitting ? t("feedback.sending") : t("feedback.submit")}
      </button>
    </form>
  );
}
