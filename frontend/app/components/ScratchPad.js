"use client";

import InkCanvas from "./InkCanvas";

// Ticket #74 (2nd MVP) - a free-draw scratch area, deliberately separate from the graded
// Step boxes: no recognition, no evaluation, no persistence. Just InkCanvas's existing
// capture surface (already touch/stylus-ready, already has its own "Clear drawing"
// button) repositioned into the page's left/right margins. onStrokesChange is
// deliberately not wired to anything - nothing needs to know what gets drawn here.
export default function ScratchPad({ side }) {
  return (
    <div
      className={`hidden xl:flex fixed top-24 flex-col gap-1 ${
        side === "left" ? "left-4" : "right-4"
      }`}
    >
      <span className="text-xs font-medium uppercase tracking-wide text-gray-400">
        Kladblok
      </span>
      <InkCanvas width={220} height={520} />
    </div>
  );
}
