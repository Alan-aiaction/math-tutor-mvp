# 2026-08-22 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Continuation of the app-rename thread. Suggested "Leermaatje"/"LeerLab"
  first, then "Brainbot"/"Breinbot" once Alan asked for something that signals the
  adaptive-tutoring/AI angle directly - got as far as a full approved plan for
  "Brainbot" before Alan ran his own trademark research and found BRAINBOTS is an
  active EU registration (Yoto Ltd), Class 41, directly overlapping this product's
  category. Dropped that direction immediately - nothing had been implemented yet.

  Ran a follow-up shortlist (Botje, Bytje, Denkbot, Adapto, Nimbo, Kompas) through a
  quick web-search collision check before presenting them, per the lesson from
  Brainbot - caught Adapto (existing adaptive-learning platform) and Kompas (multiple
  existing Dutch education apps, one with real trademark licensing) as clear
  conflicts, and flagged the whole "-bot" naming pattern as increasingly crowded
  (Tutorbot, Tutrbot, Botbot all exist as real marks) even for the surviving
  candidates.

  Alan ended the search and asked to just drop "MVP" from the existing name instead -
  no new trademark exposure, since it's the same name this product has always had.
  Confirmed via AskUserQuestion that "v1.0" is an internal milestone marker only, not
  part of the displayed name. Went through EnterPlanMode (reusing the file-scoping
  work already done for the abandoned Brainbot plan) before touching code.

  Mid-implementation, discovered the branch had gone stale - both PR #136 (privacy
  attribution fix) and PR #137 (LLM token limit) had merged into master since the
  branch was cut. Rebuilt the branch from fresh master before continuing (stash,
  reset, reapply) rather than risk a stacked-PR situation.

  Straightforward text change across 7 files (layout.js, page.js, privacy/page.js,
  main.py, README.md, Architecture.md, system-design.html); grepped the whole repo
  afterward to confirm only the 8 intentionally-untouched historical/technical files
  still say "Math Tutor MVP". Frontend suite green (58/58), backend suite green
  (285/285), `next build` clean with the rendered `<title>` confirmed as "Math Tutor".
