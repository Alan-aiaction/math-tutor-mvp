// Mocked stand-in for POST /attempts/check (task #45 swaps this for the real call).
// Shaped like the EvaluationResult model from docs/architecture/api_contract_draft_20260728.md.
const MOCK_RESULTS_CYCLE = [
  { valid: true, misconception_id: null, hint_text: null },
  {
    valid: false,
    misconception_id: "unlike-denominators",
    hint_text: "Check that both fractions share the same denominator before adding them.",
  },
];

export function mockCheckWork(steps) {
  return steps.map((_, index) => MOCK_RESULTS_CYCLE[index % MOCK_RESULTS_CYCLE.length]);
}
