"use client";

import InkCanvas from "./InkCanvas";

// Ticket #74 (2nd MVP) - a free-draw scratch area, deliberately separate from the graded
// Step boxes: no recognition, no evaluation, no persistence. Just InkCanvas's existing
// capture surface (already touch/stylus-ready, already has its own "Clear drawing"
// button) repositioned into the page's left/right margins. onStrokesChange is
// deliberately not wired to anything - nothing needs to know what gets drawn here.
//
// Fixed pixel size, not CSS-responsive (InkCanvas's stroke coordinates are computed
// directly from the canvas's own pixel rect - scaling the element via CSS without
// scaling those coordinates would misalign drawn strokes from the pointer). 320x640
// sized up from an initial 220x520 after live tablet-width testing showed real unused
// margin space beyond that - see ticket #74's board card.
export default function ScratchPad({ side }) {
  return (
    <div
      className={`hidden xl:flex fixed top-20 flex-col gap-1 ${
        side === "left" ? "left-6" : "right-6"
      }`}
    >
      <span className="text-xs font-medium uppercase tracking-wide text-gray-400">
        Kladblok
      </span>
      <InkCanvas width={320} height={640} />
    </div>
  );
}
