"use client";

import { useLanguage } from "../lib/LanguageContext";

export function overallAccuracy(trend) {
  if (!trend.length) return null;
  return trend.reduce((sum, day) => sum + day.accuracy, 0) / trend.length;
}

export function formatPercent(value) {
  return value === null ? "–" : `${Math.round(value * 100)}%`;
}

// Extracted from Dashboard.jsx (own-data-only child dashboard, see MyProgress.jsx) -
// the hero title, KPI cards, trend chart, and weak-spot list are identical for both a
// parent viewing one child's numbers and a child viewing their own - only what's above
// this (Dashboard.jsx's comparison table, which a child must never see) differs.
export default function ProgressSummary({ child, kpis }) {
  const { t } = useLanguage();
  const accuracy = overallAccuracy(kpis.accuracy_trend);

  return (
    <>
      <section className="flex flex-col gap-1 rounded-2xl border border-border bg-bg p-6">
        <span className="text-xs font-bold uppercase tracking-wide text-warm">{t("dashboard.eyebrow")}</span>
        <h1 className="font-display text-2xl font-bold text-ink">
          {t("dashboard.heroFor", { name: child.nickname })}
        </h1>
      </section>

      <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard label={t("dashboard.kpiAccuracy")} figure={formatPercent(accuracy)} />
        <KpiCard label={t("dashboard.kpiDays")} figure={kpis.practice_frequency_days} />
        <KpiCard label={t("dashboard.kpiRetries")} figure={kpis.average_retries.toFixed(1)} />
        <KpiCard label={t("dashboard.kpiTotal")} figure={kpis.total_attempts} />
      </section>

      <section className="rounded-2xl border border-border bg-bg p-6">
        <h2 className="font-display text-base font-bold text-ink">{t("dashboard.trendTitle")}</h2>
        <TrendChart trend={kpis.accuracy_trend} />
      </section>

      <section className="rounded-2xl border border-border bg-bg p-6">
        <h2 className="font-display text-base font-bold text-ink">{t("dashboard.weakspotTitle")}</h2>
        <p className="text-xs text-ink-muted">{t("dashboard.weakspotSub")}</p>
        <div className="mt-3 flex flex-col gap-3">
          {kpis.weak_spots_by_topic.map((spot) => (
            <div key={spot.topic} className="flex flex-col gap-1">
              <div className="flex justify-between text-sm">
                <span data-testid="weakspot-topic" className="font-bold text-ink">
                  {spot.topic}
                </span>
                <span className="text-ink-muted">{formatPercent(spot.accuracy)}</span>
              </div>
              <div className="h-1.5 rounded-full bg-surface-2">
                <div
                  className={`h-full rounded-full ${spot.accuracy < 0.7 ? "bg-warn" : "bg-primary"}`}
                  style={{ width: `${Math.round(spot.accuracy * 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

function KpiCard({ label, figure }) {
  return (
    <div className="flex flex-col gap-1 rounded-2xl border border-border bg-bg p-4">
      <span className="text-xs font-bold text-ink-muted">{label}</span>
      <span className="font-display text-2xl font-bold text-ink">{figure}</span>
    </div>
  );
}

function TrendChart({ trend }) {
  const { t } = useLanguage();
  if (!trend.length) return <p className="mt-3 text-sm text-ink-muted">{t("dashboard.noData")}</p>;

  const width = 480;
  const height = 120;
  const step = trend.length > 1 ? width / (trend.length - 1) : 0;
  const points = trend.map((day, i) => {
    const x = trend.length > 1 ? i * step : width / 2;
    const y = height - day.accuracy * height;
    return { x, y };
  });
  const linePath = points.map((p) => `${p.x},${p.y}`).join(" ");

  return (
    <svg className="mt-3 w-full" width="100%" height={height} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
      <polyline points={linePath} fill="none" stroke="var(--color-primary)" strokeWidth="2.5" />
      {points.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r={i === points.length - 1 ? 4 : 3} fill="var(--color-primary)" />
      ))}
    </svg>
  );
}
