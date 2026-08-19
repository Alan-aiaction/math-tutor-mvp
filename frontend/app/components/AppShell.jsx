"use client";

import { useState } from "react";
import { useLanguage } from "../lib/LanguageContext";

// 3rd MVP: real navigation shell, replacing page.js's old three-way full-screen branch.
// Oefenen is only reachable once a child is active (mirrors the ouder-dashboard mockup's
// data-mode rule) - Dashboard and Mijn kinderen are reachable regardless, so a parent can
// check progress without first launching a practice session. Logo/nav icons are dashed
// placeholder slots, same as the mockup - real assets land once design work is done.
export default function AppShell({ activeChild, view, onNavigate, onSignOut, children }) {
  const { t } = useLanguage();
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    activeChild ? { key: "oefenen", label: t("nav.oefenen") } : null,
    { key: "dashboard", label: t("nav.dashboard") },
    { key: "kinderen", label: t("nav.mijnkinderen") },
  ].filter(Boolean);

  return (
    <div className="flex min-h-screen">
      <aside
        className={`flex flex-col gap-6 bg-sidebar p-4 text-white ${collapsed ? "w-20" : "w-60"}`}
      >
        <div className="flex items-center gap-2">
          <div className="flex flex-1 items-center gap-2 rounded-xl border border-dashed border-white/40 p-2 text-white/60">
            <div className="h-7 w-7 flex-shrink-0 rounded-lg border border-dashed border-white/40" />
            {!collapsed && <span className="text-xs font-bold uppercase tracking-wide">Logo</span>}
          </div>
          <button
            type="button"
            onClick={() => setCollapsed((prev) => !prev)}
            aria-expanded={!collapsed}
            aria-label={t("nav.menu")}
            className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg border border-white/20 hover:bg-white/10"
          >
            ☰
          </button>
        </div>

        <nav className="flex flex-1 flex-col gap-1">
          {!collapsed && (
            <p className="px-2 pb-1 text-xs font-bold uppercase tracking-wide text-white/60">
              {t("nav.menu")}
            </p>
          )}
          {navItems.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={() => onNavigate?.(item.key)}
              aria-current={view === item.key ? "page" : "false"}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-bold ${
                view === item.key ? "bg-sidebar-active text-white" : "text-white/90 hover:bg-white/10"
              } ${collapsed ? "justify-center" : ""}`}
            >
              <span className="h-5 w-5 flex-shrink-0 rounded border border-dashed border-white/40" />
              {!collapsed && item.label}
            </button>
          ))}
        </nav>

        <div className="flex flex-col gap-1 border-t border-white/10 pt-3">
          <button
            type="button"
            onClick={() => onNavigate?.("account")}
            aria-current={view === "account" ? "page" : "false"}
            className={`flex items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-bold ${
              view === "account" ? "bg-sidebar-active text-white" : "text-white/90 hover:bg-white/10"
            } ${collapsed ? "justify-center" : ""}`}
          >
            <span className="h-5 w-5 flex-shrink-0 rounded border border-dashed border-white/40" />
            {!collapsed && t("nav.account")}
          </button>
          <button
            type="button"
            onClick={onSignOut}
            className={`flex items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-bold text-white/90 hover:bg-white/10 ${
              collapsed ? "justify-center" : ""
            }`}
          >
            <span className="h-5 w-5 flex-shrink-0 rounded border border-dashed border-white/40" />
            {!collapsed && t("nav.uitloggen")}
          </button>
        </div>
      </aside>

      <div className="flex flex-1 flex-col bg-surface">
        <div className="flex items-center gap-3 border-b border-border bg-bg px-8 py-3">
          <div className="flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1.5 text-sm font-bold text-ink">
            <span className="h-6 w-6 flex-shrink-0 rounded-full border border-dashed border-ink-muted" />
            {activeChild ? activeChild.nickname : t("topbar.workingAs").split(":")[0]}
          </div>
          <div className="flex-1" />
          <span className="h-8 w-8 flex-shrink-0 rounded-full border border-dashed border-ink-muted" />
        </div>

        {/* relative (fix PR #118 regression): ScratchPad positions itself absolute
            within this element instead of fixed-to-viewport, so it tracks the content
            pane's real bounds instead of colliding with the sidebar at any width. */}
        <main className="relative flex-1 p-8">{children}</main>
      </div>
    </div>
  );
}
