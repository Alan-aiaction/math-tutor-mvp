"use client";

import InkCanvas from "./InkCanvas";

// Ticket #74 (2nd MVP) - a free-draw scratch area, deliberately separate from the graded
// Step boxes: no recognition, no evaluation, no persistence. Just InkCanvas's existing
// capture surface (already touch/stylus-ready, already has its own "Clear drawing"
// button) repositioned into the page's left/right margins. onStrokesChange is
// deliberately not wired to anything - nothing needs to know what gets drawn here.
//
// Responsive sizing (follow-up to the original fixed 320x640): the panel's box is sized
// by real viewport space (clamped width, top/bottom-anchored height) and InkCanvas's
// opt-in `responsive` mode measures that box and resizes its own canvas to match,
// redrawing existing strokes rather than losing them - see InkCanvas.js and
// docs/architecture/tablet_scratch_pad_design.md for why. `lg:` (1024px), not the
// original `xl:` (1280px) - real iPad landscape widths (~1080-1366px depending on model)
// sit below 1280px, so `xl:` meant these panels never actually showed on the target
// device. iPad portrait (all models <=1024px) still has no room for two panels plus the
// centered step content, so this stays landscape-only by design.
export default function ScratchPad({ side }) {
  return (
    <div
      className={`hidden lg:flex fixed top-20 bottom-6 flex-col gap-1 ${
        side === "left" ? "left-6" : "right-6"
      }`}
      style={{ width: "clamp(140px, 14vw, 340px)" }}
    >
      <span className="text-xs font-medium uppercase tracking-wide text-gray-400">
        Kladblok
      </span>
      <InkCanvas responsive />
    </div>
  );
}
