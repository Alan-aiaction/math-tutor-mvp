# 2026-08-10 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: added ticket #65 ("Next problem" button after checking
  work) to the board - a real gap found via live testing right after #64 merged. #64 only
  randomizes the problem on initial page load; there's no in-app way to get a different
  problem afterward (only a manual browser refresh). Board entry only in this PR - the
  implementation is planned separately next.
