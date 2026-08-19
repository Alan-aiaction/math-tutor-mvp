"use client";

import { useState } from "react";
import InkCanvas from "./InkCanvas";
import { apiFetch } from "../lib/apiFetch";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL;
const CANVAS_WIDTH = 400;
const CANVAS_HEIGHT = 160;

const STATUS_STYLES = {
  unanswered: {
    border: "border-gray-300",
    badge: "bg-gray-100 text-gray-500",
    icon: null,
    label: "Unanswered",
  },
  correct: {
    border: "border-green-400",
    badge: "bg-green-100 text-green-700",
    icon: "✓",
    label: "Correct",
  },
  incorrect: {
    border: "border-amber-400",
    badge: "bg-amber-100 text-amber-700",
    icon: "⚠",
    label: "Incorrect",
  },
};

export default function StepBox({ index, status = "unanswered", recognizedLatex = "", result = null, onDelete, onChange }) {
  const effectiveStatus = result ? (result.valid ? "correct" : "incorrect") : status;
  const style = STATUS_STYLES[effectiveStatus] ?? STATUS_STYLES.unanswered;
  const [value, setValue] = useState(recognizedLatex);
  const [draft, setDraft] = useState(recognizedLatex);
  const [editing, setEditing] = useState(false);
  const [drawing, setDrawing] = useState(false);
  const [strokeGroups, setStrokeGroups] = useState([]);
  const [recognizing, setRecognizing] = useState(false);
  const [recognizeError, setRecognizeError] = useState(null);

  const startEdit = () => {
    setDraft(value);
    setEditing(true);
  };

  const confirmEdit = () => {
    setValue(draft);
    onChange?.(draft);
    setEditing(false);
  };

  const startDrawing = () => {
    setStrokeGroups([]);
    setRecognizeError(null);
    setDrawing(true);
  };

  const recognizeDrawing = async () => {
    if (strokeGroups.length === 0) return;
    setRecognizing(true);
    setRecognizeError(null);
    try {
      const data = await apiFetch(`${BACKEND_URL}/recognize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ strokeGroups, width: CANVAS_WIDTH, height: CANVAS_HEIGHT }),
      });
      setValue(data.latex);
      onChange?.(data.latex);
      setDrawing(false);
    } catch (err) {
      setRecognizeError(err.message || "Recognition failed");
    } finally {
      setRecognizing(false);
    }
  };

  return (
    <div className={`rounded-lg border-2 p-4 ${style.border}`}>
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm font-medium text-gray-700">Step {index + 1}</span>
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${style.badge}`}>
            {style.icon && <span aria-hidden="true">{style.icon}</span>}
            {style.label}
          </span>
          {onDelete && (
            <button
              type="button"
              onClick={onDelete}
              aria-label={`Delete step ${index + 1}`}
              className="text-gray-400 transition-colors hover:text-red-500"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      <div className="mt-3 border-t border-gray-100 pt-3 text-left">
        {drawing ? (
          <div className="flex flex-col gap-2">
            <InkCanvas width={CANVAS_WIDTH} height={CANVAS_HEIGHT} onStrokesChange={setStrokeGroups} />
            {recognizeError && <p className="text-xs text-red-600">{recognizeError}</p>}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={recognizeDrawing}
                disabled={strokeGroups.length === 0 || recognizing}
                className="rounded bg-emerald-600 px-3 py-1 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-40"
              >
                {recognizing ? "Recognising…" : "Recognise"}
              </button>
              <button
                type="button"
                onClick={() => setDrawing(false)}
                className="text-xs font-medium text-gray-500 hover:underline"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : editing ? (
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              aria-label={`Edit recognised value for step ${index + 1}`}
              className="flex-1 rounded border border-gray-300 px-2 py-1 text-sm"
            />
            <button
              type="button"
              onClick={confirmEdit}
              className="rounded bg-emerald-600 px-3 py-1 text-xs font-medium text-white hover:bg-emerald-700"
            >
              Confirm
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-between gap-2">
            <span className="text-sm text-gray-600">
              Recognised as: <span className="font-mono">{value || "—"}</span>
            </span>
            {/* Once a step is correct, it's locked - no more Draw/Edit. Matches the
                mental model that answering correctly finishes that step, rather than
                leaving it editable forever with no end state. Delete still works
                regardless (see the ✕ button above) - removing a step entirely is a
                different action from editing its content. */}
            {effectiveStatus !== "correct" && (
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={startDrawing}
                  className="text-xs font-medium text-blue-600 hover:underline"
                >
                  Draw
                </button>
                <button
                  type="button"
                  onClick={startEdit}
                  className="text-xs font-medium text-blue-600 hover:underline"
                >
                  Edit
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {result && !result.valid && result.hint_text && (
        <div className="mt-3 rounded-md bg-amber-50 p-3 text-left text-sm text-amber-800">
          <span className="font-medium">Hint:</span> {result.hint_text}
        </div>
      )}
    </div>
  );
}
