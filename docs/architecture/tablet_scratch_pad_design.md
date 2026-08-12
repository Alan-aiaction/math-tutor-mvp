# Tablet scratch pad design (ticket #74)

## What this is

A free-draw area on tablet/iPad, alongside the graded Step boxes, with zero recognition
and zero evaluation. Lets a student use the screen the way they'd use paper — side
calculations, notes, doodles-while-thinking — without any of it touching the graded flow.

## Why it exists

Approved 2026-08-12, in a meeting where Alan showed Jeff and Richard the 1st MVP status
deck, the 2nd MVP task board, and a live demo — all approved. This was the one new feature
requested: a tablet-friendly scratch surface outside the formal Step/answer area. It's an
explicit, one-time exception to 2nd MVP's otherwise backend-only scope (the board's
Overview tab lists "GUI/UI improvements" as out of scope generally) — this feature is
carved out by name, not a reopening of that boundary.

## Layout

Two independent scratch panels, fixed to the page's left and right margins:

```
┌───────────┬──────────────────────────────┬───────────┐
│           │        Math Tutor MVP         │           │
│           │        Your code / Problem    │           │
│  Kladblok │        Step 1                 │  Kladblok │
│  (left)   │        Step 2 ...              │  (right)  │
│           │        + Add / Check / Clear / │           │
│           │        Next problem            │           │
└───────────┴──────────────────────────────┴───────────┘
```

- **Two panels, not one** — a left- or right-handed student can use whichever side is
  natural; a note and a calculation can live in different places without competing for
  space.
- **Fixed position, not in normal document flow** — the central step list grows as steps
  are added ("+ Add next step"), which would push a below-steps panel around; the side
  margins don't have that problem.
- **Shown only on wide/tablet viewports** (`lg:` breakpoint, 1024px, and up) — there's no
  room for this on a phone-sized screen, and the request was specifically about
  tablet/iPad use. Below the breakpoint, the panels simply don't render.

## Sizing (revised - responsive, not fixed pixels)

The original implementation (live-tested 2026-08-12) used a fixed 320×640px panel gated
behind Tailwind's `xl:` (1280px) breakpoint. Checking real iPad CSS viewport widths after
that test surfaced two real problems with those numbers, not just a "could be tuned"
tuning gap:

- **The breakpoint itself was wrong for the target device.** Every iPad in portrait
  orientation, and most models even in landscape, are under 1280px wide (iPad Mini/Air
  landscape ≈1080–1180px; iPad Pro 11"/12.9" landscape ≈1194–1366px). At `xl:`, the
  panels would never show on the actual device this ticket is for, except the single
  largest iPad Pro model in landscape.
- **Fixed pixels can't fit the real range of tablet widths** even where the panels did
  show — 320px per side plus centered step content doesn't consistently fit realistic
  iPad viewport widths.

**Revised to true responsive sizing:**

- The panel's box uses `clamp(140px, 14vw, 340px)` for width, and is anchored between
  `top-20`/`bottom-6` for height (real available viewport height, not a guessed `vh`
  percentage) — both driven by the actual viewport, not a fixed guess from one
  screenshot.
- `InkCanvas.js` gained an **opt-in** `responsive` prop. When absent/false (unchanged
  default — `StepBox.js`'s exact existing usage), it renders identically to before:
  fixed `width`/`height` attributes, byte-for-byte the same code path. Only `ScratchPad`
  passes `responsive`. This is what makes the change zero-regression for `StepBox`'s
  graded recognition-drawing flow: confirmed via `grep -rn "InkCanvas" frontend/app` that
  `ScratchPad` and `StepBox` are the only two callers, and `StepBox` never opts in.
- In responsive mode, a `ResizeObserver` (native browser API, no new dependency;
  supported Safari 13.1+/iOS 13.4+) watches the canvas's wrapper element and updates the
  canvas's `width`/`height` attributes to match its real measured size on every resize
  (e.g. an iPad rotation).
- **Resize no longer silently erases a student's drawing.** Changing a `<canvas>`
  element's `width`/`height` attributes clears its drawing buffer — standard browser
  behavior. `InkCanvas` already tracks raw stroke point-data (`strokesRef`) separately
  from the rendered pixels, so every resize is followed by a redraw of every stored
  stroke onto the resized canvas, at its original absolute pixel coordinates (no
  proportional scaling — a v1 simplification: a larger canvas just shows more blank space
  around existing work, a smaller one can clip strokes at the new edge).
- **Known limitation, by design, not an oversight:** stays landscape-only. Real iPad
  portrait widths (all models ≤1024px) don't leave room for two side panels plus the
  centered step content at any reasonable size, so portrait is not supported.

**Live-verified 2026-08-13** (desktop browser, resizing the window mid-drawing): confirmed
the clip-on-shrink behavior above is real in practice, not just theoretical — a stroke
drawn near the bottom of a tall panel got cut off after shrinking the window. Decided to
accept this for 2nd MVP rather than fix now — recorded as a **revisit-later item**, not
forgotten:

| | **Keep as-is (clip on shrink) — current, 2nd MVP** | **Add proportional scaling** |
|---|---|---|
| **How it works** | No change — strokes stay at fixed pixel coordinates; shrinking loses whatever falls outside the new bounds | On every resize, remap each stroke's `x`/`y` by the ratio of new size to old size before redrawing, so drawings shrink/grow with the canvas instead of clipping |
| **Pro** | Simpler, already shipped, zero added risk | No data loss ever — resizing/rotating never drops part of a drawing |
| **Con** | A student who draws near the bottom then shrinks/rotates loses part of their drawing | Real added complexity (rescale every point on every stroke, on every resize); can distort aspect ratio if width/height don't shrink by the same proportion |

Decision: keep as-is for 2nd MVP. If this becomes a real complaint in practice, come back
to proportional scaling rather than re-deriving this comparison from scratch.

## Clear behavior

Two ways a scratch panel clears, chosen after weighing three options (auto-only /
manual-only / both — see `docs/tracking/decision-log.md` for the full comparison):

1. **Automatically, when "Next problem" fires** — the same moment steps/results already
   reset (ticket #65), so "Next problem" keeps meaning one consistent thing: everything
   about the old problem is gone, scratch work included. Implemented by keying each
   `ScratchPad` off `problem?.id`, the same remount-to-clear trick already shipped for
   `StepBox`'s ticket #65 bugfix — not new logic.
2. **Manually, at any time** — `InkCanvas`'s own built-in "Clear drawing" button, already
   present, needed no new code. Each side clears independently.

## What this explicitly is not

- **Not persisted anywhere.** Purely client-side canvas state — gone on refresh, never
  sent to the backend, no new database table or column. Confirmed directly: raw ink
  storage was already deliberately kept out of scope for the *graded* steps (#49); adding
  it here for an ungraded scratch area would reopen that same privacy-surface question for
  no real benefit.
- **Not recognized or evaluated.** No `/recognize` call, no relationship to `correct_answer`
  or `is_correct` at all.
- **Not a reopening of 2nd MVP's "no GUI work" boundary.** One named exception, not a
  precedent for further UI changes without the same explicit approval.

## Implementation

- `frontend/app/components/ScratchPad.js` — thin wrapper around the existing
  `InkCanvas.js` (already touch/stylus-ready by original design, task #48), just
  repositioned, relabeled, and (as of the sizing revision above) sized responsively.
  `onStrokesChange` deliberately left unwired.
- `frontend/app/components/InkCanvas.js` — opt-in `responsive` prop (default `false`),
  used only by `ScratchPad`; `StepBox.js` is unaffected.
- `frontend/app/page.js` — renders two `ScratchPad`s, keyed by `problem?.id`.
