import json
from datetime import datetime
from pathlib import Path

from public_health_agent import ask_public_health_agent


def load_public_health_questions():
    """
    Load the national public-health benchmark questions.

    These test cases use a real CDNA communicable-disease guideline
    and are deliberately designed to test:

    - factual retrieval,
    - conditional reasoning,
    - surveillance-data requirements,
    - evidence interpretation, and
    - hallucination resistance.
    """

    questions_path = Path(
        "data/public_health_evaluation_questions.json"
    )

    questions = json.loads(
        questions_path.read_text(
            encoding="utf-8"
        )
    )

    return questions


def run_public_health_evaluation():
    """
    Run every public-health benchmark question against the
    document-grounded measles guideline assistant.

    I preserve the raw model responses before scoring so the same
    answers can later be evaluated using different scoring methods
    without rerunning the language model.
    """

    questions = load_public_health_questions()

    results = []

    print("\n" + "=" * 70)
    print("NATIONAL PUBLIC HEALTH AI AGENT EVALUATION")
    print("=" * 70)

    print(
        f"\nRunning {len(questions)} public-health test questions...\n"
    )

    for position, test_case in enumerate(
        questions,
        start=1,
    ):

        question_id = test_case["id"]
        question = test_case["question"]

        print(
            f"[{position}/{len(questions)}] "
            f"{question_id}: {question}"
        )

        agent_answer = ask_public_health_agent(
            question
        )

        results.append(
            {
                "id": question_id,
                "category": test_case["category"],
                "question": question,
                "expected_facts":
                    test_case["expected_facts"],
                "agent_answer": agent_answer,
            }
        )

        print("Response captured.\n")

    return results


def save_public_health_run(results):
    """
    Save the raw public-health benchmark responses separately from
    the grant-program evaluation.

    This keeps the two benchmark domains distinct while allowing
    both to use the same downstream evaluator.
    """

    output_directory = Path(
        "outputs"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_path = (
        output_directory
        / f"public_health_evaluation_run_{timestamp}.json"
    )

    output_path.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path


if __name__ == "__main__":

    results = run_public_health_evaluation()

    output_path = save_public_health_run(
        results
    )

    print("=" * 70)
    print("PUBLIC HEALTH EVALUATION RUN COMPLETE")
    print("=" * 70)

    print(
        f"\nQuestions tested: {len(results)}"
    )

    print(
        f"Raw results saved to: {output_path}"
    )