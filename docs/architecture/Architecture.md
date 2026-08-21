# Math Tutor — Architecture

The maintained architecture diagram is
[`math_tutor_mvp_architecture.drawio`](math_tutor_mvp_architecture.drawio) (open in
[diagrams.net](https://app.diagrams.net) or the VS Code "Draw.io Integration"
extension). It was reviewed against the actual implementation on 2026-08-10 and
corrected where it had drifted. Corrections made: the Recognition Service's stale
"+ confidence" claim (MyScript has no confidence field to return, per ticket #21); the
Frontend tech stack wrongly listing the MyScript client SDK (ink capture is a plain
`<canvas>`, deliberately not the SDK, so `MYSCRIPT_APP_KEY`/`HMAC_KEY` stay backend-only
per #48) and TypeScript (the app is plain JavaScript); the Misconception Detector and
Tutor/Hint Service boxes being drawn as implemented when `misconception_id` is hardcoded
`null` and hints are a single static string (2nd MVP scope, not built yet); the missing
`GET /problems/random` endpoint (#64, now the primary way problems load); the
Orchestration Service's flow not matching `run_pipeline()`'s real stages; and the
security list's RLS line, which implied it was just "pending auth" rather than
structurally moot today (backend uses one shared `service_role` connection that bypasses
RLS by design — ticket #51's finding).

The previous static `Architecture.jpeg` export has been removed — it predated the
corrections above and wasn't being kept in sync. The `.drawio` file is the single source
of truth going forward.
