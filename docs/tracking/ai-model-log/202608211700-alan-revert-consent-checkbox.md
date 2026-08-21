# 2026-08-21 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Same-day follow-up on PR #136 (still open). Alan shared a screenshot of
  DeepSeek's sign-up consent notice - plain text near the button, no checkbox - and
  asked directly to revert the checkbox added earlier today and go back to the passive
  pattern, matching what Squla and Junior Einstein actually use (both already
  researched for PR #132's privacy statement; neither uses a checkbox - consent there
  is implicit in account creation itself).

  Reverted `ParentAuth.jsx` and `ParentAuth.test.jsx` to their pre-checkbox shape:
  `privacyAgreed` state removed, the notice is passive text again (sign-up mode only),
  submit re-gated on `loading` alone. Translation key reverted
  `privacyAgreePrefix` -> `privacyNoticePrefix`, passive wording restored in both
  NL/EN. Pushed as new commits onto the same PR #136 branch rather than a separate
  revert PR, since #136 hadn't merged yet.

  Frontend suite green (52/52, down from 56 - the checkbox-specific tests removed
  along with the checkbox), backend suite unaffected, `next build` clean.
