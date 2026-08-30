import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader


# ---------------------------------------------------------
# LOAD MY API KEY
# ---------------------------------------------------------
#
# I reuse the same Gemini API key stored locally in .env.
#
# The key remains outside the source code and is excluded from Git.
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found. Check the local .env file."
    )


client = genai.Client(
    api_key=api_key
)


# ---------------------------------------------------------
# LOAD THE NATIONAL PUBLIC HEALTH GUIDELINE
# ---------------------------------------------------------
#
# This benchmark uses a real Australian national communicable
# disease guideline rather than a fictional policy.
#
# The document is the CDNA National Guidelines for Public Health
# Units for measles.
pdf_path = Path(
    "data/measles_cdna_song.pdf"
)

reader = PdfReader(
    pdf_path
)


# Extract the text from every page.
pages = []

for page_number, page in enumerate(
    reader.pages,
    start=1,
):

    text = page.extract_text() or ""

    pages.append(
        f"\n--- PAGE {page_number} ---\n{text}"
    )


guideline_text = "\n".join(
    pages
)


def ask_public_health_agent(question):
    """
    Ask a document-grounded AI assistant a question about the
    national measles public-health guideline.

    The model is restricted to the supplied guideline.

    This benchmark is designed to test whether the agent can:

    - retrieve factual public-health information,
    - preserve important conditions,
    - interpret evidence carefully, and
    - avoid inventing information not contained in the guideline.
    """

    prompt = f"""
You are assisting a public-health team with questions about the
CDNA National Guidelines for Public Health Units for measles.

Answer using ONLY the guideline supplied below.

RULES:

- Do not use outside knowledge.
- Do not invent public-health requirements, penalties, timeframes
  or recommendations.
- Preserve important conditions and exceptions.
- If the guideline does not specify the answer, clearly say so.
- Keep the answer concise.
- This is a document-grounding exercise, not a substitute for
  professional or clinical judgement.


MEASLES CDNA GUIDELINE

{guideline_text}


QUESTION

{question}
""".strip()

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
    )

    return interaction.output_text.strip()


if __name__ == "__main__":

    test_question = (
        "How quickly should probable and confirmed measles "
        "cases be entered into the notifiable diseases database?"
    )

    answer = ask_public_health_agent(
        test_question
    )

    print("\nQuestion:")
    print(test_question)

    print("\nAgent answer:")
    print(answer)