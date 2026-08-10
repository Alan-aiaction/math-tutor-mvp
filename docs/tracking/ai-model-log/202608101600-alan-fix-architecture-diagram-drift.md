# 2026-08-10 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: reviewed the newly-uploaded editable architecture diagram
  (docs/architecture/math_tutor_mvp_architecture.drawio) against the actual codebase and
  fixed drift. Key corrections: Frontend tech stack wrongly listed the MyScript client SDK
  and TypeScript (ink capture is a plain canvas per #48's key-security decision; app is
  plain JavaScript); Misconception Detector and Tutor/Hint Service boxes were drawn as
  implemented when misconception_id is hardcoded null and hints are one static string
  (2nd MVP scope); missing GET /problems/random (#64), now the primary problem-load
  endpoint; Orchestration Service flow didn't match run_pipeline()'s real stages
  (parse/validate/correctness/hint/build_result); Recognition Service's stale
  "+ confidence" claim (already a documented issue on the old jpeg, same fix applied
  here); security list's RLS line implied "pending auth" rather than the real #51
  finding (structurally moot - one shared service_role connection bypasses RLS by
  design). Also updated Architecture.md to point at the new .drawio as the maintained
  version. Verified the edited .drawio still parses as valid XML.
