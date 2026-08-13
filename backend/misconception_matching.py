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
itself a parseable math expression (true for the proposal doc's fraction-addition
/fraction-subtraction examples). Word problems and non-LaTeX text (like "6 x 199"
with a plain multiplication sign, not \\times) fail to parse and this module
correctly, safely returns None rather than guessing - see #55's curriculum
coverage check (docs/architecture/slo_curriculum_coverage_groep78.md): none of
the 47 problems seeded so far are fraction problems, and misconception_rules has
0 rows until #9 seeds real content. This module is built and tested against the
proposal doc's own worked examples, ready for when #9 exists, not proven against
real production data yet.

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


_OPERAND_EXTRACTORS = {
    "fraction_addition": _extract_two_fraction_operands,
    "fraction_subtraction": _extract_two_fraction_operands,
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
