# 2026-08-13 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: tickets #30 and #31 - implemented the deterministic
  misconception rule-matching engine. #9 (real seed content) isn't done, so tested against
  the rule-format proposal doc's own two worked examples (fraction_addition,
  fraction_subtraction) instead of real seeded rules - documented deviation from #30's
  literal AC. Resolved a real, previously-unsolved design gap the proposal doc itself
  flagged as "not decided here": operand extraction needs the problem's original
  expression (Problem.question_text), not correct_answer (already simplified, operands
  gone); and rule lookup works by iterating stored rules and letting each one's own
  `operation` field select its extractor, rather than inventing a separate
  problem-to-operation classifier. Caught and fixed a real correctness bug during design
  (not shipped): sympy's Add doesn't preserve written left-to-right argument order, which
  would have silently broken subtraction operand extraction (addition is symmetric so it
  didn't matter there) - fixed by disambiguating operands by sign instead of position,
  covered by its own test. Explicitly did not wire into orchestration.py - that's #33's
  job. Ran the full 136-test backend suite after the change, zero regressions, confirmed
  evaluation_result.py's pinned `misconception_id=None` test still passes untouched. Zero
  residue in misconception_rules after integration tests. New files:
  backend/misconception_matching.py, backend/test_misconception_matching.py,
  backend/test_misconception_matching_integration.py.
