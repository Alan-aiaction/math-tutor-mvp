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
- **Shown only on wide/tablet viewports** (`xl:` breakpoint and up) — there's no room for
  this on a phone-sized screen, and the request was specifically about tablet/iPad use.
  Below the breakpoint, the panels simply don't render.

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
  repositioned and relabeled. `onStrokesChange` deliberately left unwired.
- `frontend/app/page.js` — renders two `ScratchPad`s, keyed by `problem?.id`.
