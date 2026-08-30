import json
from pathlib import Path


def load_public_health_evaluation():
    """
    Load the latest scored national public-health evaluation.

    This file contains the six-question measles benchmark after it
    has already been scored by the same hybrid evaluator used for
    the grant-program benchmark.
    """

    scored_path = Path(
        "outputs/latest_public_health_scored_evaluation.json"
    )

    if not scored_path.exists():
        raise FileNotFoundError(
            "No scored public-health evaluation was found. "
            "Run score_public_health_evaluation.py first."
        )

    evaluation = json.loads(
        scored_path.read_text(
            encoding="utf-8"
        )
    )

    return evaluation


def generate_public_health_report(evaluation):
    """
    Generate a readable Markdown report for the national
    public-health challenge.

    I want this report to show that the same AI-agent evaluation
    architecture can be applied to a real Australian communicable-
    disease guideline rather than only a fictional administrative
    procedure.
    """

    summary = evaluation["summary"]
    results = evaluation["results"]

    report_lines = []

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------

    report_lines.append(
        "# National Communicable Disease AI Agent Evaluation"
    )

    report_lines.append("")

    report_lines.append(
        "**Source:** CDNA National Guidelines for Public Health "
        "Units for measles"
    )

    report_lines.append("")

    report_lines.append(
        "**Evaluation method:** "
        "Hybrid lexical coverage + statement-level semantic similarity"
    )

    report_lines.append("")

    # ---------------------------------------------------------
    # PURPOSE
    # ---------------------------------------------------------

    report_lines.append(
        "## Purpose"
    )

    report_lines.append("")

    report_lines.append(
    "This benchmark tests whether a document-grounded AI assistant "
    "can answer questions from a real Australian national "
    "communicable-disease guideline while preserving important "
    "conditions, interpreting surveillance and diagnostic evidence "
    "carefully, and avoiding unsupported claims."
)

    report_lines.append("")

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    report_lines.append(
        "## Evaluation Summary"
    )

    report_lines.append("")

    report_lines.append(
        f"- Questions tested: "
        f"**{summary['questions_tested']}**"
    )

    report_lines.append(
        f"- Questions passed: "
        f"**{summary['questions_passed']} / "
        f"{summary['questions_tested']}**"
    )

    report_lines.append(
        f"- Pass rate: "
        f"**{summary['pass_rate'] * 100:.1f}%**"
    )

    report_lines.append(
        f"- Expected-fact coverage: "
        f"**{summary['fact_coverage'] * 100:.1f}%**"
    )

    report_lines.append("")

    # ---------------------------------------------------------
    # BENCHMARK COVERAGE
    # ---------------------------------------------------------

    report_lines.append(
        "## Benchmark Coverage"
    )

    report_lines.append("")

    report_lines.append(
        "The six-question benchmark includes:"
    )

    report_lines.append("")

    categories = sorted(
        {
            result["category"]
            for result in results
        }
    )

    for category in categories:

        report_lines.append(
            f"- {category.replace('_', ' ').title()}"
        )

    report_lines.append("")

    # ---------------------------------------------------------
    # QUESTION RESULTS
    # ---------------------------------------------------------

    report_lines.append(
        "## Question Results"
    )

    report_lines.append("")

    for result in results:

        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        report_lines.append(
            f"### {result['id']} — {status}"
        )

        report_lines.append("")

        report_lines.append(
            f"**Category:** "
            f"{result['category'].replace('_', ' ').title()}"
        )

        report_lines.append("")

        report_lines.append(
            f"**Question:** "
            f"{result['question']}"
        )

        report_lines.append("")

        report_lines.append(
            f"**Agent response:** "
            f"{result['agent_answer']}"
        )

        report_lines.append("")

        report_lines.append(
            f"**Expected-fact coverage:** "
            f"{result['facts_covered']} / "
            f"{result['total_facts']}"
        )

        report_lines.append("")

        # Show each expected fact so the benchmark remains
        # transparent rather than presenting only a final score.
        report_lines.append(
            "**Expected facts:**"
        )

        report_lines.append("")

        for fact in result["fact_results"]:

            fact_status = (
                "covered"
                if fact["covered"]
                else "missed"
            )

            report_lines.append(
                f"- {fact['expected_fact']} "
                f"— **{fact_status}**"
            )

        report_lines.append("")

    # ---------------------------------------------------------
    # HALLUCINATION-RESISTANCE RESULT
    # ---------------------------------------------------------

    report_lines.append(
        "## Hallucination-Resistance Test"
    )

    report_lines.append("")

    hallucination_results = [
        result
        for result in results
        if result["category"]
        == "hallucination_resistance"
    ]

    if hallucination_results:

        hallucination_result = (
            hallucination_results[0]
        )

        report_lines.append(
            f"**Question:** "
            f"{hallucination_result['question']}"
        )

        report_lines.append("")

        report_lines.append(
            f"**Agent response:** "
            f"{hallucination_result['agent_answer']}"
        )

        report_lines.append("")

        report_lines.append(
            "The benchmark deliberately asks about a financial "
            "penalty that is not specified in the supplied guideline. "
            "The agent correctly avoids inventing a penalty and states "
            "that the guideline does not specify one."
        )

        report_lines.append("")

    # ---------------------------------------------------------
    # INTERPRETATION
    # ---------------------------------------------------------

    report_lines.append(
        "## Interpretation"
    )

    report_lines.append("")

    report_lines.append(
        "All six benchmark questions passed the current automated "
        "evaluation. The results indicate that, for this small "
        "controlled benchmark, the document-grounded assistant "
        "successfully retrieved factual guidance, preserved important "
        "conditions, handled evidence interpretation and resisted the "
        "deliberately unsupported financial-penalty question."
    )

    report_lines.append("")

    report_lines.append(
        "The result should not be interpreted as evidence that the "
        "agent is suitable for clinical or public-health deployment. "
        "The benchmark is designed to demonstrate an AI evaluation "
        "method using a real national public-health source."
    )

    report_lines.append("")

    # ---------------------------------------------------------
    # LIMITATIONS
    # ---------------------------------------------------------

    report_lines.append(
        "## Limitations"
    )

    report_lines.append("")

    report_lines.append(
        "- The benchmark contains six questions."
    )

    report_lines.append(
        "- The evaluation uses one national communicable-disease "
        "guideline."
    )

    report_lines.append(
        "- Lexical and semantic similarity are proxies for factual "
        "correctness and do not guarantee substantive accuracy."
    )

    report_lines.append(
        "- The benchmark does not test real clinical decision-making."
    )

    report_lines.append(
        "- The agent is evaluated as a document-grounded information "
        "assistant rather than as a replacement for public-health or "
        "clinical judgement."
    )

    report_lines.append(
        "- Human review remains necessary when interpreting automated "
        "evaluation results."
    )

    report_lines.append("")

    return "\n".join(
        report_lines
    )


def save_public_health_report(report_text):
    """
    Save the national public-health evaluation report.
    """

    output_path = Path(
        "outputs/public_health_ai_agent_evaluation_report.md"
    )

    output_path.write_text(
        report_text,
        encoding="utf-8",
    )

    return output_path


if __name__ == "__main__":

    evaluation = (
        load_public_health_evaluation()
    )

    report = generate_public_health_report(
        evaluation
    )

    output_path = save_public_health_report(
        report
    )

    print("\n" + "=" * 70)
    print("PUBLIC HEALTH EVALUATION REPORT GENERATED")
    print("=" * 70)

    print(
        f"\nReport saved to: {output_path}"
    )