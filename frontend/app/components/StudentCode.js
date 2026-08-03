"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "mathTutorStudentCode";

// Frontend-only stub for task #50: a short code (not a login) that will identify this
// student's attempts once #45/#15 wire up the real backend. No format enforced - a teacher
// or student can use anything short and memorable.
export default function StudentCode({ onChange }) {
  const [code, setCode] = useState("");

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored) {
      setCode(stored);
      onChange?.(stored);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleChange = (e) => {
    const value = e.target.value;
    setCode(value);
    window.localStorage.setItem(STORAGE_KEY, value);
    onChange?.(value);
  };

  return (
    <div className="flex w-full max-w-md flex-col gap-1 text-left">
      <label
        htmlFor="student-code"
        className="text-sm font-medium uppercase tracking-wide text-gray-500"
      >
        Your code
      </label>
      <input
        id="student-code"
        type="text"
        value={code}
        onChange={handleChange}
        placeholder="e.g. your first name + a number"
        className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
      />
    </div>
  );
}
