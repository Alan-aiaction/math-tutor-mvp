"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/apiFetch";
import { useLanguage } from "../lib/LanguageContext";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;

// 3rd MVP: the "Mijn kinderen" chapter's content, living inside AppShell (no longer a
// forced full-screen gate, and no longer has its own sign-out - the shell's sidebar
// covers that globally now). Tiles for each linked child, an "add child" flow, and a
// per-child password gate - matches Squla/Junior Einstein's own shape (see
// decision-log.md's authentication-design entry). onChildSelected fires with the chosen
// child once its password gate succeeds; page.js stores that as the active child.
export default function ChildPicker({ accessToken, onChildSelected }) {
  const { t } = useLanguage();
  const [children, setChildren] = useState(null);
  const [loadError, setLoadError] = useState(null);

  const [view, setView] = useState("list"); // "list" | "add" | "gate"
  const [gatingChild, setGatingChild] = useState(null);
  const [confirmingDeleteId, setConfirmingDeleteId] = useState(null);
  const [deleteError, setDeleteError] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const authHeaders = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${accessToken}`,
  };

  const loadChildren = async () => {
    setLoadError(null);
    try {
      const data = await apiFetch(`${BACKEND_URL}/children`, { headers: authHeaders });
      setChildren(data);
    } catch (err) {
      setLoadError(err.message || t("childpicker.loadError"));
    }
  };

  useEffect(() => {
    loadChildren();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openGate = (child) => {
    setGatingChild(child);
    setView("gate");
  };

  const backToList = () => {
    setView("list");
    setGatingChild(null);
  };

  const confirmDelete = async (childId) => {
    setDeleting(true);
    setDeleteError(null);
    try {
      await apiFetch(`${BACKEND_URL}/children/${childId}`, { method: "DELETE", headers: authHeaders });
      setConfirmingDeleteId(null);
      await loadChildren();
    } catch (err) {
      setDeleteError(err.message || t("childpicker.removeError"));
    } finally {
      setDeleting(false);
    }
  };

  if (children === null && !loadError) {
    return <p className="text-sm text-ink-muted">{t("dashboard.loading")}</p>;
  }

  if (view === "add") {
    return (
      <AddChildForm
        authHeaders={authHeaders}
        onAdded={async () => {
          await loadChildren();
          setView("list");
        }}
        onCancel={() => setView("list")}
      />
    );
  }

  if (view === "gate" && gatingChild) {
    return (
      <ChildPasswordGate
        child={gatingChild}
        authHeaders={authHeaders}
        onSuccess={(child) => onChildSelected?.(child)}
        onBack={backToList}
      />
    );
  }

  return (
    <div className="flex w-full max-w-md flex-col gap-4">
      <h2 className="text-left text-sm font-bold uppercase tracking-wide text-ink-muted">
        {t("childpicker.whosWorking")}
      </h2>

      {loadError && <p className="text-sm text-warn">{loadError}</p>}

      {children && children.length === 0 && !loadError && (
        <p className="text-sm text-ink-muted">{t("childpicker.noChildren")}</p>
      )}

      {deleteError && <p className="text-sm text-warn">{deleteError}</p>}

      {children && children.length > 0 && (
        <div className="flex flex-wrap gap-3">
          {children.map((child) =>
            confirmingDeleteId === child.id ? (
              <div
                key={child.id}
                className="flex items-center gap-2 rounded-xl border-2 border-warn/40 px-3 py-2 text-sm"
              >
                <span className="text-ink">{t("childpicker.removeConfirm", { name: child.nickname })}</span>
                <button
                  type="button"
                  onClick={() => confirmDelete(child.id)}
                  disabled={deleting}
                  className="font-bold text-warn hover:underline disabled:opacity-40"
                >
                  {deleting ? t("childpicker.removing") : t("childpicker.yesRemove")}
                </button>
                <button
                  type="button"
                  onClick={() => setConfirmingDeleteId(null)}
                  className="text-ink-muted hover:underline"
                >
                  {t("childpicker.cancel")}
                </button>
              </div>
            ) : (
              <div
                key={child.id}
                className="flex items-center gap-1 rounded-xl border-2 border-border px-2 py-2 hover:border-primary"
              >
                <button type="button" onClick={() => openGate(child)} className="px-2 py-1 text-sm font-bold text-ink">
                  {child.nickname}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setDeleteError(null);
                    setConfirmingDeleteId(child.id);
                  }}
                  aria-label={t("childpicker.removeAriaLabel", { name: child.nickname })}
                  className="px-1 text-xs text-ink-muted hover:text-warn"
                >
                  ✕
                </button>
              </div>
            )
          )}
        </div>
      )}

      <button
        type="button"
        onClick={() => setView("add")}
        className="self-start rounded-xl border-2 border-dashed border-border px-4 py-2 text-sm font-bold text-ink-muted hover:border-placeholder-border"
      >
        + {t("childpicker.addChild")}
      </button>
    </div>
  );
}

function AddChildForm({ authHeaders, onAdded, onCancel }) {
  const { t } = useLanguage();
  const [nickname, setNickname] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await apiFetch(`${BACKEND_URL}/children`, {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({ nickname, password }),
      });
      onAdded?.();
    } catch (err) {
      setError(err.message || t("childpicker.addError"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="flex w-full max-w-md flex-col gap-3">
      <h2 className="text-left text-sm font-bold uppercase tracking-wide text-ink-muted">
        {t("childpicker.addChild")}
      </h2>
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
        minLength={4}
        className="rounded-xl border border-border px-3 py-2 text-sm"
      />
      {error && <p className="text-sm text-warn">{error}</p>}
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="rounded-xl bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-strong disabled:opacity-40"
        >
          {submitting ? t("parentAuth.pleaseWait") : t("childpicker.addChild")}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-xl border border-border px-4 py-2 text-sm font-bold text-ink-muted hover:bg-surface"
        >
          {t("childpicker.cancel")}
        </button>
      </div>
    </form>
  );
}

function ChildPasswordGate({ child, authHeaders, onSuccess, onBack }) {
  const { t } = useLanguage();
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const loggedInChild = await apiFetch(`${BACKEND_URL}/children/${child.id}/login`, {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({ password }),
      });
      onSuccess?.(loggedInChild);
    } catch (err) {
      // Stays on this same gate, not the whole picker - fast re-entry on a shared tablet.
      setError(err.message || t("childpicker.incorrectPassword"));
      setPassword("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="flex w-full max-w-md flex-col gap-3">
      <h2 className="text-left text-sm font-bold uppercase tracking-wide text-ink-muted">
        {child.nickname}&apos;s {t("childpicker.password").toLowerCase()}
      </h2>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder={t("childpicker.password")}
        autoFocus
        required
        className="rounded-xl border border-border px-3 py-2 text-sm"
      />
      {error && <p className="text-sm text-warn">{error}</p>}
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="rounded-xl bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-strong disabled:opacity-40"
        >
          {submitting ? t("parentAuth.pleaseWait") : t("childpicker.go")}
        </button>
        <button
          type="button"
          onClick={onBack}
          className="rounded-xl border border-border px-4 py-2 text-sm font-bold text-ink-muted hover:bg-surface"
        >
          {t("childpicker.cancel")}
        </button>
      </div>
    </form>
  );
}
