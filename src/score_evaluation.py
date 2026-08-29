import json
import re
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


# ---------------------------------------------------------
# LOAD THE SEMANTIC EVALUATION MODEL
# ---------------------------------------------------------
#
# My earlier evaluation approaches exposed two different problems.
#
# V1 used word matching.
#
# This worked well when the agent used similar terminology, but it
# incorrectly marked semantically equivalent wording such as:
#
# "Written notification"
#
# and
#
# "notified in writing"
#
# as different.
#
# V2 compared each expected fact with the agent's entire answer
# using sentence embeddings.
#
# That introduced another problem: a short expected fact could be
# diluted when compared against a much longer multi-point answer.
#
# V3 therefore combines lexical matching with statement-level
# semantic similarity.
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ---------------------------------------------------------
# TEXT NORMALISATION
# ---------------------------------------------------------


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "if",
    "in",
    "is",
    "it",
    "may",
    "must",
    "no",
    "not",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "up",
    "with",
}


def normalise_text(text):
    """
    Convert text into a simpler form for lexical comparison.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9$]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def extract_meaningful_terms(text):
    """
    Extract informative terms from an expected fact.

    These terms provide a transparent lexical signal that complements
    the semantic evaluator.
    """

    normalised = normalise_text(
        text
    )

    words = normalised.split()

    meaningful_terms = [
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 2
    ]

    return meaningful_terms


# ---------------------------------------------------------
# LEXICAL COVERAGE
# ---------------------------------------------------------


def calculate_lexical_coverage(
    expected_fact,
    agent_answer,
):
    """
    Calculate how many meaningful expected terms appear in the
    agent's answer.

    This retains the useful behaviour of my original transparent
    evaluator.
    """

    expected_terms = extract_meaningful_terms(
        expected_fact
    )

    answer_text = normalise_text(
        agent_answer
    )

    if not expected_terms:
        return 0.0

    matched_terms = [
        term
        for term in expected_terms
        if term in answer_text
    ]

    return (
        len(matched_terms)
        / len(expected_terms)
    )


# ---------------------------------------------------------
# SPLIT ANSWERS INTO STATEMENTS
# ---------------------------------------------------------


def split_answer_into_statements(answer):
    """
    Break an AI-generated answer into smaller statements.

    V2 compared a short expected fact against the entire agent
    response.

    Testing showed that this could dilute semantic similarity when
    the response contained several different facts.

    I now compare each expected fact against smaller sentences or
    bullet points and retain the strongest semantic match.
    """

    # Remove common Markdown bullet characters so they do not
    # interfere with statement extraction.
    cleaned_answer = answer.replace(
        "*",
        ""
    )

    # Split on:
    #
    # - new lines,
    # - sentence-ending punctuation.
    statements = re.split(
        r"[\n]+|(?<=[.!?])\s+",
        cleaned_answer,
    )

    # Remove empty statements.
    statements = [
        statement.strip()
        for statement in statements
        if statement.strip()
    ]

    # If splitting somehow produced nothing, fall back to the
    # original answer.
    if not statements:
        statements = [
            answer.strip()
        ]

    return statements


# ---------------------------------------------------------
# STATEMENT-LEVEL SEMANTIC SIMILARITY
# ---------------------------------------------------------


def calculate_best_semantic_similarity(
    expected_fact,
    agent_answer,
):
    """
    Compare one expected fact with each individual statement in the
    agent answer.

    I keep the highest semantic similarity because that statement is
    the strongest candidate for expressing the expected fact.
    """

    statements = split_answer_into_statements(
        agent_answer
    )

    expected_embedding = model.encode(
        expected_fact,
        convert_to_tensor=True,
    )

    statement_embeddings = model.encode(
        statements,
        convert_to_tensor=True,
    )

    similarities = cos_sim(
        expected_embedding,
        statement_embeddings,
    )[0]

    best_index = int(
        similarities.argmax()
    )

    best_similarity = float(
        similarities[best_index]
    )

    best_statement = statements[
        best_index
    ]

    return (
        best_similarity,
        best_statement,
    )


# ---------------------------------------------------------
# HYBRID FACT EVALUATION
# ---------------------------------------------------------


def score_expected_fact(
    expected_fact,
    agent_answer,
    lexical_threshold=0.6,
    semantic_threshold=0.45,
):
    """
    Evaluate whether one expected fact is covered by the agent answer.

    V3 uses two complementary signals:

    1. lexical coverage
       - useful when the expected terminology appears directly

    2. statement-level semantic similarity
       - useful when the agent expresses the same idea using
         different wording

    A fact is considered covered when either signal provides strong
    enough evidence.

    This avoids assuming that one evaluation method is always better.
    """

    lexical_score = calculate_lexical_coverage(
        expected_fact,
        agent_answer,
    )

    (
        semantic_score,
        best_statement,
    ) = calculate_best_semantic_similarity(
        expected_fact,
        agent_answer,
    )

    lexical_pass = (
        lexical_score >= lexical_threshold
    )

    semantic_pass = (
        semantic_score >= semantic_threshold
    )

    covered = (
        lexical_pass
        or semantic_pass
    )

    # Record which signal caused the fact to pass.
    if lexical_pass and semantic_pass:

        coverage_reason = (
            "lexical_and_semantic"
        )

    elif lexical_pass:

        coverage_reason = (
            "lexical"
        )

    elif semantic_pass:

        coverage_reason = (
            "semantic"
        )

    else:

        coverage_reason = (
            "not_covered"
        )

    return {
        "expected_fact":
            expected_fact,

        "lexical_score":
            round(
                lexical_score,
                3,
            ),

        "semantic_similarity":
            round(
                semantic_score,
                3,
            ),

        "best_matching_statement":
            best_statement,

        "coverage_reason":
            coverage_reason,

        "covered":
            covered,
    }


# ---------------------------------------------------------
# SCORE ONE QUESTION
# ---------------------------------------------------------


def score_question(
    result,
    lexical_threshold=0.6,
    semantic_threshold=0.45,
):
    """
    Score one agent response against all expected facts.

    Every expected fact must be covered for the question to pass.
    """

    fact_results = []

    for expected_fact in result[
        "expected_facts"
    ]:

        fact_result = score_expected_fact(
            expected_fact,
            result["agent_answer"],
            lexical_threshold,
            semantic_threshold,
        )

        fact_results.append(
            fact_result
        )

    total_facts = len(
        fact_results
    )

    covered_facts = sum(
        1
        for fact in fact_results
        if fact["covered"]
    )

    if total_facts:

        coverage_score = (
            covered_facts
            / total_facts
        )

    else:

        coverage_score = 0.0

    passed = (
        total_facts > 0
        and covered_facts == total_facts
    )

    return {
        "id":
            result["id"],

        "category":
            result["category"],

        "question":
            result["question"],

        "agent_answer":
            result["agent_answer"],

        "facts_covered":
            covered_facts,

        "total_facts":
            total_facts,

        "coverage_score":
            round(
                coverage_score,
                3,
            ),

        "passed":
            passed,

        "fact_results":
            fact_results,
    }


# ---------------------------------------------------------
# SCORE THE COMPLETE BENCHMARK
# ---------------------------------------------------------


def score_evaluation(results):
    """
    Score every response and calculate overall benchmark metrics.
    """

    scored_results = [
        score_question(
            result
        )
        for result in results
    ]

    total_questions = len(
        scored_results
    )

    passed_questions = sum(
        1
        for result in scored_results
        if result["passed"]
    )

    total_expected_facts = sum(
        result["total_facts"]
        for result in scored_results
    )

    total_covered_facts = sum(
        result["facts_covered"]
        for result in scored_results
    )

    if total_questions:

        pass_rate = (
            passed_questions
            / total_questions
        )

    else:

        pass_rate = 0.0

    if total_expected_facts:

        fact_coverage = (
            total_covered_facts
            / total_expected_facts
        )

    else:

        fact_coverage = 0.0

    summary = {
        "questions_tested":
            total_questions,

        "questions_passed":
            passed_questions,

        "questions_failed":
            total_questions
            - passed_questions,

        "pass_rate":
            round(
                pass_rate,
                3,
            ),

        "fact_coverage":
            round(
                fact_coverage,
                3,
            ),

        "evaluation_method":
            "hybrid_lexical_and_statement_semantic",

        "lexical_threshold":
            0.6,

        "semantic_threshold":
            0.45,
    }

    return (
        scored_results,
        summary,
    )


# ---------------------------------------------------------
# FIND THE LATEST RAW RUN
# ---------------------------------------------------------


def find_latest_evaluation_run():
    """
    Find the most recent raw agent evaluation run.
    """

    output_directory = Path(
        "outputs"
    )

    evaluation_files = list(
        output_directory.glob(
            "evaluation_run_*.json"
        )
    )

    if not evaluation_files:

        raise FileNotFoundError(
            "No evaluation run was found in outputs."
        )

    latest_file = max(
        evaluation_files,
        key=lambda path: path.stat().st_mtime,
    )

    return latest_file


# ---------------------------------------------------------
# SAVE SCORED RESULTS
# ---------------------------------------------------------


def save_scored_results(
    scored_results,
    summary,
):
    """
    Save detailed hybrid evaluation results separately from the raw
    agent responses.
    """

    output_directory = Path(
        "outputs"
    )

    output_path = (
        output_directory
        / "latest_scored_evaluation.json"
    )

    evaluation_output = {
        "summary":
            summary,

        "results":
            scored_results,
    }

    output_path.write_text(
        json.dumps(
            evaluation_output,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path


# ---------------------------------------------------------
# RUN THE EVALUATOR
# ---------------------------------------------------------


if __name__ == "__main__":

    evaluation_path = (
        find_latest_evaluation_run()
    )

    print(
        f"\nScoring evaluation run: "
        f"{evaluation_path}"
    )

    results = json.loads(
        evaluation_path.read_text(
            encoding="utf-8"
        )
    )

    scored_results, summary = (
        score_evaluation(
            results
        )
    )

    # ---------------------------------------------------------
    # DISPLAY QUESTION RESULTS
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("AI AGENT EVALUATION RESULTS")
    print("=" * 70)

    print(
        "\nEvaluation method: "
        "Hybrid lexical + statement-level semantic similarity"
    )

    print(
        f"Lexical threshold: "
        f"{summary['lexical_threshold']}"
    )

    print(
        f"Semantic threshold: "
        f"{summary['semantic_threshold']}"
    )

    for result in scored_results:

        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        percentage = (
            result["coverage_score"]
            * 100
        )

        print(
            f"\n{result['id']} | "
            f"{result['category']} | "
            f"{percentage:.0f}% | "
            f"{status}"
        )

        # Show detailed fact-level information for failures.
        if not result["passed"]:

            for fact in result[
                "fact_results"
            ]:

                print(
                    f"    lexical="
                    f"{fact['lexical_score']:.3f} | "
                    f"semantic="
                    f"{fact['semantic_similarity']:.3f} | "
                    f"{'COVERED' if fact['covered'] else 'MISSED'}"
                )

                print(
                    f"    Expected: "
                    f"{fact['expected_fact']}"
                )

                print(
                    f"    Best match: "
                    f"{fact['best_matching_statement']}"
                )

    # ---------------------------------------------------------
    # DISPLAY SUMMARY
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"\nQuestions tested: "
        f"{summary['questions_tested']}"
    )

    print(
        f"Questions passed: "
        f"{summary['questions_passed']}"
    )

    print(
        f"Questions failed: "
        f"{summary['questions_failed']}"
    )

    print(
        f"Pass rate: "
        f"{summary['pass_rate'] * 100:.1f}%"
    )

    print(
        f"Expected fact coverage: "
        f"{summary['fact_coverage'] * 100:.1f}%"
    )

    output_path = save_scored_results(
        scored_results,
        summary,
    )

    print(
        f"\nDetailed scores saved to: "
        f"{output_path}"
    )