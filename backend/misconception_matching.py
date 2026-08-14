"""Deterministic misconception rule-matching engine (tickets #30, #31 - 2nd MVP).

Given a problem's own expression and a student's wrong answer, checks whether any
approved misconception_rules row (see docs/architecture/
proposal_misconception_rule_format.md, Fig. 1) predicts that exact wrong value -
purely symbolic, no LLM involved. Real-time LLM classification was explicitly
rejected in that same proposal doc: it breaks the stable misconception_id this
deterministic approach needs for hint escalation.

Operand extraction ("a, b, c, d" in a wrong_result_template like "(a+c)/(b+d)")
needs the ORIGINAL problem expression, not just its final correct_answer - for
"1/3 + 1/4 = 7/12", the operands 1/3/1/4 only exist in the expression itself, not
in the already-simplified "7/12" answer. This module parses Problem.question_text
for that reason.

Real, current limitation, not hidden: this only works when question_text is
itself a parseable math expression. Word problems still fail to parse and this
module correctly, safely returns None rather than guessing. Non-LaTeX notation
like "x" for multiplication or a "$" currency sign is NOT handled (latex_parser
only fixes "x"/"E" - the two symbols actually present in the 47 seeded problems,
found and fixed alongside this ticket - not every possible non-LaTeX variant).

Extractors below fall into two groups: `fraction_addition`/`fraction_subtraction`
match the rule-format proposal doc's own worked examples but, per #55's curriculum
coverage check (docs/architecture/slo_curriculum_coverage_groep78.md), zero of
the 47 seeded problems are fraction problems - these two never match real content
today. `multiplication_near_round`/`money_decimal_multiplication`/
`multiplication_double_near_round` target what's actually seeded (compensation-
strategy multiplication, money multiplication) and back the bootstrap
misconception_rules batches drafted for ticket #9 (see docs/architecture/
misconception_rules_bootstrap_batch_1.md and _batch_2.md) - hand-authored from
known common groep 7/8 mistakes rather than from real shadow-log data, since no
real student usage exists yet (the live attempts/attempt_steps tables were
confirmed to be test residue, not real student data, and were cleared).

Still a real, current limitation, per batch 2's own investigation: the 2 seeded
word problems (division-with-remainder, price-per-kg) have no extractor at all,
by design - their operands aren't recoverable from question_text alone (the
"how many people share" or "grams per kilogram" facts live in the sentence's
meaning, not in the numbers), and neither a regex-per-sentence hack nor a schema
change was judged worth it for 2 problems. Deferred, not silently dropped.

Deliberately does NOT wire into orchestration.py's pipeline - mapping a matched
misconception_id to an actual hint is #33's job ("map misconception_id to an
approved hint"), which also needs #70's hint-variant pool. evaluation_result.py's
hardcoded `misconception_id=None` (and the two tests pinning that) stay
untouched here on purpose.
"""
import sympy

from db import get_client
from canonical_form import are_equivalent
from latex_parser import parse_math_latex, LatexParseError


def _extract_two_fraction_operands(expr):
    """From an unevaluated two-term sum/difference of fractions (a/b + c/d or
    a/b - c/d), return (a, b, c, d) - or None if expr isn't shaped like that.

    sympy.Add doesn't preserve written left-to-right order (it's commutative
    and may canonicalize the args), so this can't just read expr.args[0]/[1]
    positionally. Addition is symmetric under that reordering ((a+c)/(b+d) ==
    (c+a)/(d+b)), so it wouldn't matter there anyway - but subtraction isn't
    symmetric, so this disambiguates by sign instead: exactly one term should
    be positive (a/b) and one negative (the negated c/d), for a well-posed
    a/b - c/d expression.
    """
    if not isinstance(expr, sympy.Add) or len(expr.args) != 2:
        return None
    fractions = [sympy.nsimplify(term) for term in expr.args]
    if not all(f.is_Rational for f in fractions):
        return None

    positives = [f for f in fractions if f > 0]
    negatives = [f for f in fractions if f < 0]

    if len(positives) == 2:
        a, b = positives[0].p, positives[0].q
        c, d = positives[1].p, positives[1].q
        return a, b, c, d
    if len(positives) == 1 and len(negatives) == 1:
        a, b = positives[0].p, positives[0].q
        c, d = -negatives[0].p, negatives[0].q
        return a, b, c, d
    return None


def _nearest_round_and_diff(n: int):
    """For an integer n, find the nearest round number (a multiple of 10, 100,
    1000, ...) it's close to, and how far off it is.

    Returns (rounded, diff) where diff = rounded - n, or None if n isn't close
    to any round number (e.g. single-digit numbers, or a number already exactly
    round). "Close" here is calibrated against the real seeded factors (199,
    98, 101, 403, ... down to diffs as small as 1 and as large as 3) rather
    than a theoretical definition: within 5, or within 2% of n, whichever is
    more lenient.
    """
    n = int(n)
    if n == 0:
        return None
    best = None
    digits = len(str(abs(n)))
    for exponent in range(1, digits):
        base = 10**exponent
        rounded = round(n / base) * base
        diff = rounded - n
        if diff == 0:
            continue
        if best is None or abs(diff) < abs(best[1]):
            best = (rounded, diff)
    if best is None:
        return None
    rounded, diff = best
    if abs(diff) <= 5 or abs(diff) <= 0.02 * abs(n):
        return rounded, diff
    return None


def _extract_multiplication_near_round_operands(expr):
    """From an unevaluated two-factor product (a x b), find the factor that's
    near a round number and treat the other as the 'clean' multiplier.

    Returns (a, b, c, d) = (clean factor, messy factor, nearest round number,
    diff = rounded - messy), or None if the shape doesn't fit: not a two-factor
    product of integers, neither factor is near-round, or - a real, explicit
    gap, not silently mishandled - BOTH factors are near-round (a "double
    compensation" problem like 101 x 99 or 99 x 1001; 2 of the 20 seeded
    calculateInteger problems are shaped this way and are correctly excluded
    here rather than picking one factor to round arbitrarily).
    """
    if not isinstance(expr, sympy.Mul) or len(expr.args) != 2:
        return None
    factors = [sympy.nsimplify(f) for f in expr.args]
    if not all(f.is_Integer for f in factors):
        return None

    near_round = [(i, _nearest_round_and_diff(int(f))) for i, f in enumerate(factors)]
    near_round = [(i, result) for i, result in near_round if result is not None]
    if len(near_round) != 1:
        return None

    messy_index, (rounded, diff) = near_round[0]
    clean_index = 1 - messy_index
    a = int(factors[clean_index])
    b = int(factors[messy_index])
    return a, b, rounded, diff


def _extract_integer_times_decimal_operands(expr):
    """From an unevaluated two-factor product where one factor is a whole
    number and the other has a fractional part (e.g. 3 x 19.50), return
    (a, b, a, b) = (integer factor, decimal factor, ...) - the trailing pair
    duplicates a/b since this shape only ever needs two named operands, but
    match_misconception always unpacks a 4-tuple. Returns None if the shape
    doesn't fit (not a two-factor product, or neither/both factors are
    non-integer).
    """
    if not isinstance(expr, sympy.Mul) or len(expr.args) != 2:
        return None
    factors = [sympy.nsimplify(f, rational=True) for f in expr.args]
    integer_factors = [f for f in factors if f.is_Integer]
    decimal_factors = [f for f in factors if f.is_Rational and not f.is_Integer]
    if len(integer_factors) != 1 or len(decimal_factors) != 1:
        return None
    a = integer_factors[0]
    b = decimal_factors[0]
    return a, b, a, b


def _extract_double_compensation_operands(expr):
    """From an unevaluated two-factor product where BOTH factors are near a
    round number (e.g. 101 x 99, 99 x 1001 - the "double compensation" shape
    _extract_multiplication_near_round_operands deliberately excludes), return
    (r1, d1, r2, d2): each factor's nearest round number and diff (rounded -
    messy), reusing _nearest_round_and_diff. Returns None if the shape doesn't
    fit: not a two-factor integer product, or fewer than both factors are
    near-round (the single-near-round case is handled by the other extractor).

    Known, explicit limitation: sympy.Mul.args order isn't guaranteed to match
    how the problem was written (unlike the Add-with-signs case in
    _extract_two_fraction_operands, there's no sign here to disambiguate which
    factor is "first") - so a rule about compensating only one specific side
    can't be built on top of this without arbitrarily guessing which. Only the
    symmetric "forgot both compensations" misconception is drafted against
    this extractor's output for that reason.
    """
    if not isinstance(expr, sympy.Mul) or len(expr.args) != 2:
        return None
    factors = [sympy.nsimplify(f) for f in expr.args]
    if not all(f.is_Integer for f in factors):
        return None

    near_round = [_nearest_round_and_diff(int(f)) for f in factors]
    if any(result is None for result in near_round):
        return None

    (r1, d1), (r2, d2) = near_round
    return r1, d1, r2, d2


_OPERAND_EXTRACTORS = {
    "fraction_addition": _extract_two_fraction_operands,
    "fraction_subtraction": _extract_two_fraction_operands,
    "multiplication_near_round": _extract_multiplication_near_round_operands,
    "money_decimal_multiplication": _extract_integer_times_decimal_operands,
    "multiplication_double_near_round": _extract_double_compensation_operands,
}


def match_misconception(question_text: str, wrong_expr) -> str | None:
    """Check every approved misconception rule against this problem + wrong answer.

    `question_text` is the problem's own expression (not correct_answer - see
    module docstring for why operand extraction needs the original expression).
    `wrong_expr` is the student's wrong answer, already parsed to a SymPy
    expression by the caller (same parse the Evaluator pipeline already does
    before calling correctness_check.is_correct - not re-parsed here).

    Returns the first matching rule's id, or None if nothing matches -
    including when question_text itself isn't parseable math (word problems),
    which is a real and expected case here, not an error (ticket #31's AC).
    """
    try:
        problem_expr = parse_math_latex(question_text)
    except LatexParseError:
        return None

    client = get_client()
    rules = client.table("misconception_rules").select("*").execute().data

    for rule in rules:
        matching_rule = rule["matching_rule"]
        extractor = _OPERAND_EXTRACTORS.get(matching_rule["operation"])
        if extractor is None:
            continue
        operands = extractor(problem_expr)
        if operands is None:
            continue
        a, b, c, d = operands
        template = matching_rule["check"]["wrong_result_template"]
        predicted_wrong = sympy.sympify(template, locals={"a": a, "b": b, "c": c, "d": d})
        if are_equivalent(predicted_wrong, wrong_expr):
            return rule["id"]

    return None
