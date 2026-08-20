"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/apiFetch";
import { useLanguage } from "../lib/LanguageContext";
import ProgressSummary from "./ProgressSummary";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;

// A child's own dashboard - own-data-only, reachable from their independent (or
// parent-tile-tap) session with no parent involvement needed. Deliberately does not
// fetch GET /children (the sibling list) or render Dashboard.jsx's comparison table -
// a child must never see another child's progress, even their own sibling's.
export default function MyProgress({ child, token }) {
  const { t } = useLanguage();
  const [kpis, setKpis] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setError(null);
      try {
        const data = await apiFetch(`${BACKEND_URL}/children/${child.id}/kpis`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!cancelled) setKpis(data);
      } catch (err) {
        if (!cancelled) setError(err.message || t("dashboard.error"));
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [child.id, token]);

  if (error) {
    return <p className="text-sm text-warn">{error}</p>;
  }

  if (kpis === null) {
    return <p className="text-sm text-ink-muted">{t("dashboard.loading")}</p>;
  }

  return (
    <div className="flex w-full max-w-4xl flex-col gap-5">
      <ProgressSummary child={child} kpis={kpis} />
    </div>
  );
}
