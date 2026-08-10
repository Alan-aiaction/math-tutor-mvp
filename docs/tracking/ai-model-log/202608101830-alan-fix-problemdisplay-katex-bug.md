# 2026-08-10 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: fixed the ProblemDisplay.js rendering bug found earlier -
  question_text (plain English sentences) was being run through katex.renderToString(),
  which garbled word-problem text (italicized, spacing collapsed) since KaTeX assumes
  math-mode input. Removed the KaTeX call entirely; renders questionText as plain text.
  Frontend production build verified clean, and the page's bundle size dropped from
  79.9 kB to 3.54 kB, confirming KaTeX is no longer pulled into that route.
