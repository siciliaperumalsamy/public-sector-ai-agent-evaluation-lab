import json
from pathlib import Path

from score_evaluation import (
    score_evaluation,
)


def find_latest_public_health_run():
    """
    Find the most recent raw public-health evaluation run.

    I keep this separate from the grant benchmark so both domains
    can be evaluated independently using the same scoring engine.
    """

    output_directory = Path(
        "outputs"
    )

    evaluation_files = list(
        output_directory.glob(
            "public_health_evaluation_run_*.json"
        )
    )

    if not evaluation_files:
        raise FileNotFoundError(
            "No public-health evaluation run was found."
        )

    latest_file = max(
        evaluation_files,
        key=lambda path: path.stat().st_mtime,
    )

    return latest_file


def save_public_health_scores(
    scored_results,
    summary,
):
    """
    Save the scored national public-health benchmark separately
    from the grant-program benchmark.
    """

    output_path = Path(
        "outputs/latest_public_health_scored_evaluation.json"
    )

    output = {
        "summary": summary,
        "results": scored_results,
    }

    output_path.write_text(
        json.dumps(
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path


if __name__ == "__main__":

    evaluation_path = (
        find_latest_public_health_run()
    )

    print(
        f"\nScoring public-health evaluation run: "
        f"{evaluation_path}"
    )

    results = json.loads(
        evaluation_path.read_text(
            encoding="utf-8"
        )
    )

    scored_results, summary = score_evaluation(
        results
    )

    print("\n" + "=" * 70)
    print("NATIONAL PUBLIC HEALTH AI EVALUATION RESULTS")
    print("=" * 70)

    for result in scored_results:

        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        print(
            f"\n{result['id']} | "
            f"{result['category']} | "
            f"{result['coverage_score'] * 100:.0f}% | "
            f"{status}"
        )

        if not result["passed"]:

            for fact in result["fact_results"]:

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

    output_path = save_public_health_scores(
        scored_results,
        summary,
    )

    print(
        f"\nDetailed scores saved to: "
        f"{output_path}"
    )