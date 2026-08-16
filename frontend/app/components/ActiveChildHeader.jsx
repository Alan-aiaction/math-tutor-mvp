"use client";

// 3rd MVP: small persistent header shown once a child is active. "Switch child" clears
// the active child only - the parent stays signed in, returns to the picker. Without
// this there'd be no way back to the picker short of clearing localStorage by hand.
export default function ActiveChildHeader({ nickname, onSwitchChild }) {
  return (
    <div className="flex w-full max-w-md items-center justify-between rounded-lg bg-gray-50 px-4 py-2">
      <span className="text-sm font-medium text-gray-700">Working as: {nickname}</span>
      <button
        type="button"
        onClick={onSwitchChild}
        className="text-xs font-medium text-blue-600 hover:underline"
      >
        Switch child
      </button>
    </div>
  );
}
