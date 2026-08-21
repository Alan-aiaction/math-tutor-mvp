"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/apiFetch";
import { useLanguage } from "../lib/LanguageContext";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;

// 3rd MVP: the "Account" chapter's content - the language switch, plus (independent
// child login groundwork, PR 1 of 3) the family code a parent hands their child so they
// can log in on their own device without needing this parent session at all. Language
// names stay in their own language regardless of which is currently active ("Nederlands"/
// "English" never translate themselves), matching how language pickers conventionally work.
export default function Account({ accessToken }) {
  const { lang, setLang, t } = useLanguage();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setError(null);
      try {
        const data = await apiFetch(`${BACKEND_URL}/parents/me`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        if (!cancelled) setProfile(data);
      } catch (err) {
        if (!cancelled) setError(err.message || t("account.familyCodeError"));
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken]);

  const copyCode = async () => {
    if (!profile) return;
    await navigator.clipboard.writeText(profile.family_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex w-full max-w-md flex-col gap-4">
      <h2 className="font-display text-lg font-bold text-ink">{t("account.title")}</h2>

      <div className="flex flex-col gap-1 rounded-2xl border border-border bg-bg p-6">
        <span className="text-xs font-bold text-ink-muted">{t("account.languageLabel")}</span>
        <p className="text-xs text-ink-muted">{t("account.languageSub")}</p>
        <div className="mt-2 flex gap-2">
          <button
            type="button"
            onClick={() => setLang("nl")}
            aria-pressed={lang === "nl"}
            className={`rounded-xl border px-4 py-2 text-sm font-bold ${
              lang === "nl" ? "border-primary bg-primary text-white" : "border-border text-ink"
            }`}
          >
            {t("account.dutch")}
          </button>
          <button
            type="button"
            onClick={() => setLang("en")}
            aria-pressed={lang === "en"}
            className={`rounded-xl border px-4 py-2 text-sm font-bold ${
              lang === "en" ? "border-primary bg-primary text-white" : "border-border text-ink"
            }`}
          >
            {t("account.english")}
          </button>
        </div>
      </div>

      <div className="flex flex-col gap-1 rounded-2xl border border-border bg-bg p-6">
        <span className="text-xs font-bold text-ink-muted">{t("account.familyCodeLabel")}</span>
        <p className="text-xs text-ink-muted">{t("account.familyCodeSub")}</p>
        {error && <p className="mt-2 text-sm text-warn">{error}</p>}
        {!profile && !error && (
          <p className="mt-2 text-sm text-ink-muted">{t("account.familyCodeLoading")}</p>
        )}
        {profile && (
          <>
            <div className="mt-2 flex items-center gap-3">
              <span className="font-display text-2xl font-bold tracking-widest text-ink">
                {profile.family_code}
              </span>
              <button
                type="button"
                onClick={copyCode}
                className="rounded-xl border border-border px-3 py-1.5 text-xs font-bold text-ink hover:bg-surface"
              >
                {copied ? t("account.familyCodeCopied") : t("account.familyCodeCopy")}
              </button>
            </div>
            <p className="mt-1 text-xs text-ink-muted">
              {t("account.childrenUsed", { used: profile.children_count, max: profile.max_children })}
            </p>
          </>
        )}
      </div>

      <a
        href="/privacy"
        target="_blank"
        rel="noopener noreferrer"
        className="text-xs font-bold text-primary hover:underline"
      >
        {t("privacy.linkLabel")}
      </a>
    </div>
  );
}
