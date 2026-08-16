"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/apiFetch";
import { supabase } from "../lib/supabaseClient";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;

// 3rd MVP: shown once a parent session exists. Tiles for each linked child, an "add
// child" flow, and a per-child password gate - matches Squla/Junior Einstein's own shape
// (see decision-log.md's authentication-design entry). onChildSelected fires with the
// chosen child once its password gate succeeds; page.js stores that as the active child.
export default function ChildPicker({ accessToken, onChildSelected, onSignOut }) {
  const [children, setChildren] = useState(null);
  const [loadError, setLoadError] = useState(null);

  const [view, setView] = useState("list"); // "list" | "add" | "gate"
  const [gatingChild, setGatingChild] = useState(null);

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
      setLoadError(err.message || "Could not load your children");
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

  if (children === null && !loadError) {
    return <p className="text-sm text-gray-500">Loading your children…</p>;
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
      <div className="flex items-center justify-between">
        <h2 className="text-left text-sm font-medium uppercase tracking-wide text-gray-500">
          Who&apos;s working today?
        </h2>
        <button
          type="button"
          onClick={() => supabase.auth.signOut().then(() => onSignOut?.())}
          className="text-xs font-medium text-gray-500 hover:underline"
        >
          Sign out
        </button>
      </div>

      {loadError && <p className="text-sm text-red-600">{loadError}</p>}

      {children && children.length === 0 && !loadError && (
        <p className="text-sm text-gray-600">No children yet — add your first one below.</p>
      )}

      {children && children.length > 0 && (
        <div className="flex flex-wrap gap-3">
          {children.map((child) => (
            <button
              key={child.id}
              type="button"
              onClick={() => openGate(child)}
              className="rounded-lg border-2 border-gray-300 px-4 py-3 text-sm font-medium text-gray-700 hover:border-emerald-500"
            >
              {child.nickname}
            </button>
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={() => setView("add")}
        className="self-start rounded-lg border-2 border-dashed border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:border-gray-400"
      >
        + Add child
      </button>
    </div>
  );
}

function AddChildForm({ authHeaders, onAdded, onCancel }) {
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
      setError(err.message || "Could not add this child");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="flex w-full max-w-md flex-col gap-3">
      <h2 className="text-left text-sm font-medium uppercase tracking-wide text-gray-500">
        Add a child
      </h2>
      <input
        type="text"
        value={nickname}
        onChange={(e) => setNickname(e.target.value)}
        placeholder="Nickname"
        required
        className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
        minLength={4}
        className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
      />
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-40"
        >
          {submitting ? "Adding…" : "Add child"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

function ChildPasswordGate({ child, authHeaders, onSuccess, onBack }) {
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
      setError(err.message || "Incorrect password");
      setPassword("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="flex w-full max-w-md flex-col gap-3">
      <h2 className="text-left text-sm font-medium uppercase tracking-wide text-gray-500">
        {child.nickname}&apos;s password
      </h2>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        autoFocus
        required
        className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
      />
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-40"
        >
          {submitting ? "Checking…" : "Go"}
        </button>
        <button
          type="button"
          onClick={onBack}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50"
        >
          Back
        </button>
      </div>
    </form>
  );
}
