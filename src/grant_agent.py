import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# ---------------------------------------------------------
# LOAD MY API KEY
# ---------------------------------------------------------
#
# My Gemini API key is stored locally in .env rather than directly
# inside the source code.
#
# This keeps credentials separate from the application and prevents
# the key from being accidentally committed to a public repository.
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found. Check the local .env file."
    )


# Create the Gemini client.
client = genai.Client(
    api_key=api_key
)


# ---------------------------------------------------------
# LOAD THE AUTHORITATIVE PROCEDURE
# ---------------------------------------------------------
#
# For this evaluation, the grant administration procedure is the
# only source the AI agent is allowed to use.
#
# Because I know exactly what this document contains, I can later
# test whether the agent's answers are accurate, complete and
# grounded in the supplied source.
procedure_path = Path(
    "data/grant_program_procedure.txt"
)

procedure_text = procedure_path.read_text(
    encoding="utf-8"
)


def ask_grant_agent(question):
    """
    Ask the grant-program AI agent a question.

    I want the agent to behave like an internal staff assistant
    answering questions about the grant administration procedure.

    The agent is deliberately restricted to the supplied procedure.

    If the procedure does not contain enough information to answer,
    the agent should acknowledge that rather than inventing an answer.
    """

    prompt = f"""
You are an internal government grant-program assistant.

Answer the staff member's question using ONLY the administration
procedure supplied below.

RULES:

- Do not use outside knowledge.
- Do not invent requirements, approvals, exceptions or timeframes.
- If the procedure does not contain enough information to answer,
  clearly state that the procedure does not specify the answer.
- Preserve important conditions, limits and exceptions.
- Keep the answer concise and practical.
- Do not claim that something is permitted unless the procedure
  supports that conclusion.


GRANT PROGRAM ADMINISTRATION PROCEDURE

{procedure_text}


STAFF QUESTION

{question}
""".strip()

    # Send the controlled procedure and question to the model.
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
    )

    return interaction.output_text.strip()


# ---------------------------------------------------------
# MANUAL TEST
# ---------------------------------------------------------
#
# Before building the automated evaluation harness, I want to make
# sure the agent itself is working.
#
# I'm deliberately testing a question involving a funding threshold
# because the answer requires the agent to apply a specific rule
# from the procedure.


if __name__ == "__main__":

    test_question = (
        "Who approves an application for $180,000?"
    )

    answer = ask_grant_agent(
        test_question
    )

    print("\nQuestion:")
    print(test_question)

    print("\nAgent answer:")
    print(answer)