"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { translations } from "./translations";

const STORAGE_KEY = "mathTutorLanguage";
const DEFAULT_LANG = "nl";

const LanguageContext = createContext(null);

function interpolate(template, params) {
  if (!params) return template;
  return Object.keys(params).reduce(
    (text, key) => text.replaceAll(`{${key}}`, params[key]),
    template
  );
}

// Plain React Context, same "read localStorage in an effect after mount" pattern
// page.js already uses for childSession - avoids a server/client hydration mismatch
// (localStorage doesn't exist during Next.js's server render).
export function LanguageProvider({ children }) {
  const [lang, setLangState] = useState(DEFAULT_LANG);

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored && translations[stored]) setLangState(stored);
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = (next) => {
    setLangState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  };

  // Missing keys fall back to the key itself rather than throwing - a missing
  // translation shouldn't be able to crash the app.
  const t = (key, params) => interpolate(translations[lang]?.[key] ?? key, params);

  return <LanguageContext.Provider value={{ lang, setLang, t }}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within a LanguageProvider");
  return ctx;
}
