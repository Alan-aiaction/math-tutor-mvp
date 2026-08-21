"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/apiFetch";
import { useLanguage } from "../lib/LanguageContext";
import ProgressSummary, { formatPercent, overallAccuracy } from "./ProgressSummary";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;

// 3rd MVP: the "Dashboard" chapter's content, consuming the already-built
// GET /children/{child_id}/kpis endpoint (ticket "KPI data layer"). The comparison
// table always covers every child, matching the ouder-dashboard mockup's layout - this
// is a parent-only view for exactly that reason (see MyProgress.jsx for a child's own,
// own-data-only equivalent, which deliberately has no comparison table at all).
//
// Retire-active-child: the hero/KPI cards used to personalize to activeChild - now that
// concept is gone entirely (every practice session is its own separate child session,
// never represented here), so this owns its own local "which child am I looking at"
// state instead, defaulting to the first child. Purely a viewing choice - clicking a
// different child's row below can never affect anyone's practice session, by
// construction, since there's nothing here that could.
export default function Dashboard({ accessToken }) {
  const { t } = useLanguage();
  const [children, setChildren] = useState(null);
  const [kpisByChildId, setKpisByChildId] = useState({});
  const [viewedChildId, setViewedChildId] = useState(null);
  const [error, setError] = useState(null);

  const authHeaders = { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` };

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setError(null);
      try {
        const childList = await apiFetch(`${BACKEND_URL}/children`, { headers: authHeaders });
        if (cancelled) return;
        const kpisList = await Promise.all(
          childList.map((child) => apiFetch(`${BACKEND_URL}/children/${child.id}/kpis`, { headers: authHeaders }))
        );
        if (cancelled) return;
        const byId = {};
        childList.forEach((child, i) => {
          byId[child.id] = kpisList[i];
        });
        setChildren(childList);
        setKpisByChildId(byId);
      } catch (err) {
        if (!cancelled) setError(err.message || t("dashboard.error"));
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken]);

  if (error) {
    return <p className="text-sm text-warn">{error}</p>;
  }

  if (children === null) {
    return <p className="text-sm text-ink-muted">{t("dashboard.loading")}</p>;
  }

  const heroChild = children.find((c) => c.id === viewedChildId) ?? children[0];
  const heroKpis = heroChild ? kpisByChildId[heroChild.id] : null;

  if (!heroChild || !heroKpis) {
    return <p className="text-sm text-ink-muted">{t("dashboard.noData")}</p>;
  }

  return (
    <div className="flex w-full max-w-4xl flex-col gap-5">
      {children.length > 1 && (
        <div className="flex gap-2">
          {children.map((child) => (
            <button
              key={child.id}
              type="button"
              onClick={() => setViewedChildId(child.id)}
              aria-current={child.id === heroChild.id ? "page" : "false"}
              className={`rounded-xl px-4 py-2 text-sm font-bold ${
                child.id === heroChild.id
                  ? "bg-primary text-white"
                  : "border border-border text-ink hover:bg-surface"
              }`}
            >
              {child.nickname}
            </button>
          ))}
        </div>
      )}

      <ProgressSummary child={heroChild} kpis={heroKpis} />

      {children.length > 1 && (
        <section className="rounded-2xl border border-border bg-bg p-6">
          <h2 className="font-display text-base font-bold text-ink">{t("dashboard.tableTitle")}</h2>
          <p className="text-xs text-ink-muted">{t("dashboard.tableSub")}</p>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="text-xs uppercase text-ink-muted">
                  <th className="pb-2">{t("dashboard.th.child")}</th>
                  <th className="pb-2">{t("dashboard.th.accuracy")}</th>
                  <th className="pb-2">{t("dashboard.th.days")}</th>
                  <th className="pb-2">{t("dashboard.th.retries")}</th>
                  <th className="pb-2">{t("dashboard.th.focus")}</th>
                </tr>
              </thead>
              <tbody>
                {children.map((child) => {
                  const kpis = kpisByChildId[child.id];
                  const worstSpot = kpis.weak_spots_by_topic[0];
                  const isViewed = child.id === heroChild.id;
                  return (
                    <tr
                      key={child.id}
                      onClick={() => setViewedChildId(child.id)}
                      aria-current={isViewed ? "true" : "false"}
                      className={`cursor-pointer border-t border-border hover:bg-surface ${
                        isViewed ? "bg-surface" : ""
                      }`}
                    >
                      <td className="py-2 font-bold text-ink">{child.nickname}</td>
                      <td className="py-2">{formatPercent(overallAccuracy(kpis.accuracy_trend))}</td>
                      <td className="py-2">{kpis.practice_frequency_days}</td>
                      <td className="py-2">{kpis.average_retries.toFixed(1)}</td>
                      <td className="py-2">{worstSpot ? worstSpot.topic : t("dashboard.noFocus")}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
