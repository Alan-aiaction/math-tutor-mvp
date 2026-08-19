"use client";

import { useLanguage } from "../lib/LanguageContext";

// 3rd MVP: the "Account" chapter's content - just the language switch for now. Language
// names stay in their own language regardless of which is currently active ("Nederlands"/
// "English" never translate themselves), matching how language pickers conventionally work.
export default function Account() {
  const { lang, setLang, t } = useLanguage();

  return (
    <div className="flex w-full max-w-md flex-col gap-4 rounded-2xl border border-border bg-bg p-6">
      <h2 className="font-display text-lg font-bold text-ink">{t("account.title")}</h2>
      <div className="flex flex-col gap-1">
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
    </div>
  );
}
