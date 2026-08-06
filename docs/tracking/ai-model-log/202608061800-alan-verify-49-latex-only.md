# 2026-08-06 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: re-verified #49 (store LaTeX only, not raw ink) now that #13/#15
  are built, per that ticket's own board note. Confirmed structurally, not just observed:
  `attempt_steps` has no column a raw stroke could go into, and neither `recognition.py` nor
  #15's request models ever carry stroke data past the `/recognize` call. No code changes —
  verification only, task board card closed with concrete evidence.
