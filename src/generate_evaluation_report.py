import json
from pathlib import Path


# ---------------------------------------------------------
# LOAD THE LATEST SCORED EVALUATION
# ---------------------------------------------------------


def load_scored_evaluation():
    """
    Load the latest scored evaluation produced by my hybrid evaluator.

    The scored JSON contains both the overall benchmark results and
    detailed question-level results.
    """

    scored_path = Path(
        "outputs/latest_scored_evaluation.json"
    )

    if not scored_path.exists():
        raise FileNotFoundError(
            "No scored evaluation was found. "
            "Run score_evaluation.py first."
        )

    evaluation = json.loads(
        scored_path.read_text(
            encoding="utf-8"
        )
    )

    return evaluation


# ---------------------------------------------------------
# CALCULATE HALLUCINATION-RESISTANCE PERFORMANCE
# ---------------------------------------------------------


def calculate_hallucination_metrics(results):
    """
    Calculate performance on benchmark questions specifically
    designed to test unsupported assumptions and hallucination
    resistance.

    Rather than introducing another AI evaluator, I use the categories
    deliberately built into the benchmark dataset.

    These tests examine whether the agent avoids inventing information
    when the source procedure does not support the user's assumption.
    """

    hallucination_categories = {
        "unsupported_assumption",
        "hallucination_resistance",
    }

    hallucination_tests = [
        result
        for result in results
        if result["category"] in hallucination_categories
    ]

    tests_run = len(
        hallucination_tests
    )

    tests_passed = sum(
        1
        for result in hallucination_tests
        if result["passed"]
    )

    if tests_run:
        pass_rate = tests_passed / tests_run
    else:
        pass_rate = 0.0

    return {
        "tests_run": tests_run,
        "tests_passed": tests_passed,
        "tests_failed": tests_run - tests_passed,
        "pass_rate": round(
            pass_rate,
            3,
        ),
    }


# ---------------------------------------------------------
# GENERATE MARKDOWN REPORT
# ---------------------------------------------------------


def generate_markdown_report(evaluation):
    """
    Generate a readable evaluation report from the benchmark results.

    I want the report to show more than a single accuracy number.

    It therefore includes:

    - overall benchmark performance,
    - expected-fact coverage,
    - hallucination-resistance performance,
    - performance by test category,
    - failed automated tests,
    - and known limitations of the evaluator itself.
    """

    summary = evaluation["summary"]
    results = evaluation["results"]

    hallucination_metrics = (
        calculate_hallucination_metrics(
            results
        )
    )

    report_lines = []

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------

    report_lines.append(
        "# AI Agent Evaluation Report"
    )

    report_lines.append("")

    report_lines.append(
        "**System under test:** "
        "Government grant-program policy assistant"
    )

    report_lines.append("")

    report_lines.append(
        "**Evaluation method:** "
        "Hybrid lexical coverage + statement-level semantic similarity"
    )

    report_lines.append("")

    # ---------------------------------------------------------
    # EXECUTIVE SUMMARY
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
        f"- Automated questions passed: "
        f"**{summary['questions_passed']} / "
        f"{summary['questions_tested']}**"
    )

    report_lines.append(
        f"- Automated pass rate: "
        f"**{summary['pass_rate'] * 100:.1f}%**"
    )

    report_lines.append(
        f"- Expected-fact coverage: "
        f"**{summary['fact_coverage'] * 100:.1f}%**"
    )

    report_lines.append(
        f"- Hallucination-resistance tests passed: "
        f"**{hallucination_metrics['tests_passed']} / "
        f"{hallucination_metrics['tests_run']}**"
    )

    report_lines.append("")

    # ---------------------------------------------------------
    # BENCHMARK DESIGN
    # ---------------------------------------------------------

    report_lines.append(
        "## Benchmark Design"
    )

    report_lines.append("")

    report_lines.append(
        "The benchmark contains deliberately varied question types "
        "rather than testing only simple factual retrieval."
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
    # PERFORMANCE BY CATEGORY
    # ---------------------------------------------------------

    report_lines.append(
        "## Performance by Category"
    )

    report_lines.append("")

    for category in categories:

        category_results = [
            result
            for result in results
            if result["category"] == category
        ]

        category_passed = sum(
            1
            for result in category_results
            if result["passed"]
        )

        report_lines.append(
            f"- **{category.replace('_', ' ').title()}:** "
            f"{category_passed}/{len(category_results)} passed"
        )

    report_lines.append("")

    # ---------------------------------------------------------
    # HALLUCINATION RESISTANCE
    # ---------------------------------------------------------

    report_lines.append(
        "## Hallucination and Unsupported-Assumption Tests"
    )

    report_lines.append("")

    report_lines.append(
        "Two benchmark questions deliberately ask the agent about "
        "information or authority that the source procedure does not "
        "provide."
    )

    report_lines.append("")

    hallucination_results = [
        result
        for result in results
        if result["category"] in {
            "unsupported_assumption",
            "hallucination_resistance",
        }
    ]

    for result in hallucination_results:

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
            f"**Question:** {result['question']}"
        )

        report_lines.append("")

        report_lines.append(
            f"**Agent response:** {result['agent_answer']}"
        )

        report_lines.append("")

    # ---------------------------------------------------------
    # AUTOMATED FAILURES
    # ---------------------------------------------------------

    report_lines.append(
        "## Automated Evaluation Failures"
    )

    report_lines.append("")

    failed_results = [
        result
        for result in results
        if not result["passed"]
    ]

    if not failed_results:

        report_lines.append(
            "No automated benchmark failures were recorded."
        )

        report_lines.append("")

    else:

        for result in failed_results:

            report_lines.append(
                f"### {result['id']} — "
                f"{result['category'].replace('_', ' ').title()}"
            )

            report_lines.append("")

            report_lines.append(
                f"**Question:** {result['question']}"
            )

            report_lines.append("")

            report_lines.append(
                f"**Agent response:** {result['agent_answer']}"
            )

            report_lines.append("")

            report_lines.append(
                f"**Expected-fact coverage:** "
                f"{result['facts_covered']} / "
                f"{result['total_facts']}"
            )

            report_lines.append("")

            # Show exactly which expected facts the automated
            # evaluator considered missed.
            missed_facts = [
                fact
                for fact in result["fact_results"]
                if not fact["covered"]
            ]

            if missed_facts:

                report_lines.append(
                    "**Facts marked as missed:**"
                )

                report_lines.append("")

                for fact in missed_facts:

                    report_lines.append(
                        f"- {fact['expected_fact']}"
                    )

                    report_lines.append(
                        f"  - Lexical score: "
                        f"{fact['lexical_score']:.3f}"
                    )

                    report_lines.append(
                        f"  - Semantic similarity: "
                        f"{fact['semantic_similarity']:.3f}"
                    )

                    report_lines.append(
                        f"  - Best matching statement: "
                        f"{fact['best_matching_statement']}"
                    )

                report_lines.append("")

    # ---------------------------------------------------------
    # MANUAL REVIEW NOTE
    # ---------------------------------------------------------

    report_lines.append(
        "## Evaluator Review"
    )

    report_lines.append("")

    report_lines.append(
        "The remaining automated failure demonstrates a limitation "
        "of the evaluation method rather than a confirmed failure of "
        "the AI agent."
    )

    report_lines.append("")

    report_lines.append(
        "For Q09, the expected fact uses the phrase "
        "**\"written notification\"**, while the agent states that "
        "unsuccessful applicants must be **\"notified in writing\"**. "
        "These are substantively equivalent, but the hybrid evaluator "
        "does not currently score that phrasing above either configured "
        "coverage threshold."
    )

    report_lines.append("")

    report_lines.append(
        "The evaluation thresholds were not lowered after observing "
        "this result simply to produce a perfect benchmark score. "
        "The false negative is retained to make the remaining "
        "limitation of the evaluator visible."
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
        "- The benchmark currently contains 12 test questions."
    )

    report_lines.append(
        "- The source procedure is a controlled fictional document."
    )

    report_lines.append(
        "- Lexical and semantic similarity are proxies for factual "
        "correctness and do not guarantee that an answer is correct."
    )

    report_lines.append(
        "- Semantic similarity thresholds may produce both false "
        "positive and false negative evaluations."
    )

    report_lines.append(
        "- Hallucination testing currently uses deliberately designed "
        "benchmark questions rather than exhaustive unsupported-claim "
        "detection."
    )

    report_lines.append(
        "- Human review remains necessary when interpreting automated "
        "AI evaluation results."
    )

    report_lines.append("")

    return "\n".join(
        report_lines
    )


# ---------------------------------------------------------
# SAVE REPORT
# ---------------------------------------------------------


def save_report(report_text):
    """
    Save the final Markdown evaluation report.
    """

    output_path = Path(
        "outputs/ai_agent_evaluation_report.md"
    )

    output_path.write_text(
        report_text,
        encoding="utf-8",
    )

    return output_path


# ---------------------------------------------------------
# RUN REPORT GENERATION
# ---------------------------------------------------------


if __name__ == "__main__":

    evaluation = load_scored_evaluation()

    report = generate_markdown_report(
        evaluation
    )

    output_path = save_report(
        report
    )

    print("\n" + "=" * 70)
    print("EVALUATION REPORT GENERATED")
    print("=" * 70)

    print(
        f"\nReport saved to: {output_path}"
    )