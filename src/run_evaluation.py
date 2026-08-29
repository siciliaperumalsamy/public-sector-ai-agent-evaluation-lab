import json
from datetime import datetime
from pathlib import Path

from grant_agent import ask_grant_agent


def load_evaluation_questions():
    """
    Load the evaluation dataset I created for the grant-program agent.

    Each test case contains:

    - a question for the AI agent,
    - the facts I expect a good answer to contain, and
    - a category describing the type of behaviour being tested.

    Keeping the evaluation dataset separate from the agent means I can
    change or expand the tests without changing the agent itself.
    """

    questions_path = Path(
        "data/evaluation_questions.json"
    )

    questions = json.loads(
        questions_path.read_text(
            encoding="utf-8"
        )
    )

    return questions


def run_evaluation():
    """
    Run every question in the evaluation dataset against the AI agent.

    Rather than manually testing one question at a time, I want a
    repeatable evaluation run that captures every agent response.

    At this stage I am only collecting results.

    I deliberately separate response collection from scoring so I can
    inspect exactly what the agent produced before deciding how those
    responses should be evaluated.
    """

    questions = load_evaluation_questions()

    results = []

    print("\n" + "=" * 70)
    print("AI AGENT EVALUATION RUN")
    print("=" * 70)

    print(
        f"\nRunning {len(questions)} test questions...\n"
    )

    # Work through every test case in the benchmark dataset.
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

        # Ask the actual AI agent.
        agent_answer = ask_grant_agent(
            question
        )

        # Preserve both the expected information and the actual
        # model response.
        #
        # This gives the evaluation layer everything it will need
        # when I introduce scoring.
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


def save_evaluation_run(results):
    """
    Save the complete evaluation run as structured JSON.

    I want raw model responses preserved separately from any scores
    or conclusions I calculate later.

    This creates an auditable record of what the agent actually said
    during a particular evaluation run.
    """

    output_directory = Path(
        "outputs"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Include a timestamp so future evaluation runs do not
    # automatically overwrite previous results.
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_path = (
        output_directory
        / f"evaluation_run_{timestamp}.json"
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

    # Run the complete benchmark against the AI agent.
    results = run_evaluation()

    # Save the raw responses before introducing any scoring.
    output_path = save_evaluation_run(
        results
    )

    print("=" * 70)
    print("EVALUATION RUN COMPLETE")
    print("=" * 70)

    print(
        f"\nQuestions tested: {len(results)}"
    )

    print(
        f"Raw results saved to: {output_path}"
    )