# I need access to the source-code folder because the functions
# I'm testing live inside src rather than an installed package.
import sys
from pathlib import Path


project_root = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(project_root / "src"),
)


from score_evaluation import (
    calculate_lexical_coverage,
    split_answer_into_statements,
    score_expected_fact,
)


def test_exact_fact_is_covered():
    """
    Check that a clearly stated expected fact is recognised.

    This protects the basic behaviour of the evaluator.
    """

    expected_fact = (
        "The application must not proceed to full assessment"
    )

    agent_answer = (
        "The application must not proceed to full assessment."
    )

    result = score_expected_fact(
        expected_fact,
        agent_answer,
    )

    assert result["covered"] is True


def test_statement_splitting_preserves_relevant_fact():
    """
    Check that a multi-point AI response is broken into smaller
    statements before semantic comparison.

    I introduced statement-level comparison because comparing a
    short expected fact against an entire long answer diluted
    semantic similarity.
    """

    answer = (
        "The application must not proceed to full assessment.\n"
        "* The applicant may be contacted once.\n"
        "* The applicant has 10 business days to respond."
    )

    statements = split_answer_into_statements(
        answer
    )

    assert any(
        "contacted once" in statement.lower()
        for statement in statements
    )


def test_lexical_signal_catches_contacted_once():
    """
    Check that the lexical component correctly recognises a fact
    that the earlier whole-answer semantic evaluator missed.

    This reproduces the Q05 issue that motivated the hybrid
    evaluation approach.
    """

    expected_fact = (
        "The applicant may be contacted once"
    )

    agent_answer = (
        "The applicant may be contacted once to provide "
        "the missing documentation within 10 business days."
    )

    lexical_score = calculate_lexical_coverage(
        expected_fact,
        agent_answer,
    )

    assert lexical_score >= 0.6


def test_known_paraphrase_remains_visible_as_evaluator_limitation():
    """
    Preserve the known Q09 evaluator limitation.

    'Written notification' and 'notified in writing' are
    substantively equivalent, but the current configured evaluator
    does not reliably mark this pair as covered.

    I keep this behaviour visible rather than lowering thresholds
    after seeing the benchmark result simply to obtain 100%.
    """

    expected_fact = (
        "Written notification"
    )

    agent_answer = (
        "Unsuccessful applicants must be notified in writing."
    )

    result = score_expected_fact(
        expected_fact,
        agent_answer,
    )

    assert result["covered"] is False