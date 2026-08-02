# Math Tutor MVP — Architecture

![Architecture diagram](Architecture.jpeg)

## Known inaccuracy in the diagram

The **Recognition Service** box says it "Converts ink strokes to LaTeX + confidence."
That's stale: on 2026-08-01 the team resolved (ticket #21 on the task board) that
MyScript's math recognition API has no confidence field to return. The actual
`/recognize` endpoint (ticket #19, done) returns `{ latex }` only — the frontend
always shows a Confirm/Edit step instead of thresholding on a confidence score.

Everything else in the diagram (endpoints, data layer, tech stack, security notes)
matches the current task board and implementation as of 2026-08-02.
