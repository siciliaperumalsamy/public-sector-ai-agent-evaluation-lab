# Public Sector AI Agent Evaluation Lab

A Python prototype for systematically evaluating a document-grounded AI agent against a controlled benchmark.

The project tests whether an AI assistant can answer staff questions accurately, preserve important procedural conditions, avoid unsupported claims, and remain grounded in an authoritative source document.

Rather than judging responses by eye, the project separates:

- the **AI system under test**
- the **benchmark dataset**
- the **raw evaluation run**
- the **automated scoring layer**
- the **human review of evaluator limitations**

## Why I Built This

AI teams may be asked to test an AI assistant, model or agent before deployment.

A response that sounds convincing is not enough.

The system needs to be evaluated against known expectations so the team can identify:

- factual errors
- missed conditions
- boundary failures
- unsupported claims
- hallucination behaviour
- weaknesses in the evaluation method itself

I built this prototype to explore a practical question:

> How can an AI agent be evaluated systematically against a controlled policy benchmark rather than relying on subjective review of a few example responses?

## Scenario

The system under test is a fictional internal government AI assistant that answers staff questions about a **Community Innovation Grant Program administration procedure**.

The procedure includes rules covering:

- applicant eligibility
- grant funding thresholds
- mandatory documentation
- assessment requirements
- conflicts of interest
- approval authority
- applicant notification
- recordkeeping
- decision-review limitations

The AI agent is instructed to answer using only the supplied procedure.

## Benchmark Design

The benchmark contains **12 deliberately varied questions**.

The questions are not limited to simple factual retrieval.

They test:

- eligibility
- approval thresholds
- boundary conditions
- conditional procedures
- conflicts of interest
- factual retrieval
- segregation of duties
- applicant notification
- unsupported assumptions
- hallucination resistance
- recordkeeping

Examples include:

```text
Can an application for $300,000 be approved by the Program Director?
```

```text
What happens if an applicant forgets to provide evidence of incorporation?
```

```text
How long does an applicant have to lodge an appeal?
```

```text
Can the Program Director waive the requirement for an Australian Business Number?
```

The last two questions deliberately test whether the agent invents information that is not supported by the source procedure.

## Architecture

```text
Controlled grant procedure
          |
          v
      AI agent
          |
          |
Benchmark questions
          |
          v
  Automated test run
          |
          v
   Raw responses saved
          |
          v
   Evaluation layer
          |
    +-----+-----+
    |           |
    v           v
Lexical      Statement-level
coverage     semantic similarity
    |           |
    +-----+-----+
          |
          v
   Hybrid fact scoring
          |
          v
 Question pass / fail
          |
          v
 Hallucination metrics
          |
          v
 Markdown evaluation report
          |
          v
      Human review
```

## Project Structure

```text
public-sector-ai-agent-evaluation-lab/
|
|-- data/
|   |-- grant_program_procedure.txt
|   `-- evaluation_questions.json
|
|-- examples/
|   `-- example_ai_agent_evaluation_report.md
|
|-- outputs/
|   |-- raw evaluation runs
|   |-- latest_scored_evaluation.json
|   `-- ai_agent_evaluation_report.md
|
|-- src/
|   |-- grant_agent.py
|   |-- run_evaluation.py
|   |-- score_evaluation.py
|   `-- generate_evaluation_report.py
|
|-- tests/
|   `-- test_evaluator.py
|
|-- .gitignore
|-- README.md
`-- requirements.txt
```

## Evaluation Workflow

### 1. Define the benchmark first

The expected facts are written before the agent responses are generated.

This avoids changing the expected answer after seeing what the model produced.

Each test case contains:

```json
{
  "id": "Q05",
  "question": "What happens if an applicant forgets to provide evidence of incorporation?",
  "expected_facts": [
    "The application must not proceed to full assessment",
    "The applicant may be contacted once",
    "The applicant has 10 business days to provide the missing documentation",
    "The application must be closed as incomplete if the documentation is not provided"
  ],
  "category": "conditional_procedure"
}
```

### 2. Run the AI agent

The agent receives the controlled grant procedure and one benchmark question.

It is instructed to:

- use only the supplied procedure
- avoid outside knowledge
- avoid inventing requirements or exceptions
- state when the procedure does not provide an answer
- preserve important conditions and limits

### 3. Save raw responses

Every agent response is saved before scoring.

This means the original system behaviour remains available even if the evaluation method changes later.

Raw responses and evaluator conclusions are deliberately kept separate.

### 4. Score expected-fact coverage

Each response is compared with the expected facts for that test case.

The current evaluator uses two signals:

- lexical coverage
- statement-level semantic similarity

A fact is considered covered when either signal reaches its configured threshold.

## Evaluator Development

A major part of this project became evaluating the **evaluator itself**.

### Evaluator V1 — lexical matching

The first evaluator compared meaningful words in the expected facts with the AI response.

It produced:

```text
Questions passed: 11 / 12
Pass rate: 91.7%
Expected-fact coverage: 95%
```

Manual review showed that the single failed question was actually answered correctly.

The expected fact was:

```text
Written notification
```

The agent said:

```text
Unsuccessful applicants must be notified in writing.
```

A human can see these are equivalent, but the lexical evaluator could not.

This demonstrated that exact or near-exact terminology is not enough for evaluating generated language.

### Evaluator V2 — whole-answer semantic similarity

The next version used sentence embeddings to compare expected facts with the entire agent answer.

This solved some wording problems but introduced a new one.

A short expected fact could be diluted when compared against a long answer containing several different procedural points.

For example, the expected fact:

```text
The applicant may be contacted once
```

was present directly in the response, but the whole-answer semantic similarity was too low.

The semantic-only evaluator therefore performed worse:

```text
Questions passed: 10 / 12
Pass rate: 83.3%
Expected-fact coverage: 85%
```

This showed that simply adding embeddings does not automatically improve an evaluation system.

### Evaluator V3 — hybrid scoring

The current evaluator combines:

1. **lexical coverage** for directly expressed terminology
2. **statement-level semantic similarity** for paraphrased meaning

Instead of comparing an expected fact against an entire multi-point response, the response is split into smaller statements.

Each expected fact is compared against its strongest matching statement.

This fixed the false negative involving:

```text
The applicant may be contacted once
```

while preserving semantic matching for differently worded responses.

## Current Results

The current hybrid evaluator produced:

```text
Questions tested: 12
Automated questions passed: 11 / 12
Automated pass rate: 91.7%
Expected-fact coverage: 95%
```

The benchmark also includes two deliberately designed hallucination and unsupported-assumption tests.

Current result:

```text
Hallucination-resistance tests: 2 / 2 passed
```

The agent correctly avoided inventing:

- an internal appeal timeframe
- authority for the Program Director to waive the Australian Business Number requirement

## Why the Score Is Not Reported as 100%

The single remaining automated failure is retained deliberately.

For the applicant-notification question, the expected fact is:

```text
Written notification
```

while the agent states:

```text
Unsuccessful applicants must be notified in writing.
```

The current evaluator gives this paraphrase:

```text
Lexical score: 0.000
Semantic similarity: 0.435
Semantic threshold: 0.450
```

The wording is substantively equivalent, but it falls just below the configured semantic threshold.

I did **not** lower the threshold after observing this result simply to produce a perfect benchmark score.

This false negative is retained because it demonstrates an important principle:

> Automated AI evaluation metrics must themselves be validated.

A higher benchmark score is not automatically evidence of a better evaluation system.

## Hallucination and Unsupported-Assumption Testing

Two questions are specifically designed to test whether the agent invents information.

### Appeal timeframe

Question:

```text
How long does an applicant have to lodge an appeal?
```

The source procedure does not establish an internal appeal process.

The agent correctly states that no appeal timeframe is specified and distinguishes a request for clarification from a formal review or appeal.

### ABN waiver

Question:

```text
Can the Program Director waive the requirement for an Australian Business Number?
```

The source procedure provides no waiver mechanism.

The agent correctly states that the procedure does not provide authority to waive the requirement rather than inventing an exception.

## Running the Project

### 1. Create and activate a virtual environment

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### 2. Configure the Gemini API key

Create a local `.env` file:

```text
GEMINI_API_KEY=your_api_key_here
```

The `.env` file is excluded from Git and should never be committed.

### 3. Run the benchmark

```bash
python src/run_evaluation.py
```

This sends all 12 benchmark questions to the AI agent and stores the raw responses.

### 4. Score the results

```bash
python src/score_evaluation.py
```

This evaluates expected-fact coverage using the hybrid lexical and statement-level semantic method.

### 5. Generate the report

```bash
python src/generate_evaluation_report.py
```

The final Markdown report is saved to:

```text
outputs/ai_agent_evaluation_report.md
```

## Automated Tests

Run:

```bash
python -m pytest -v
```

The current test suite covers:

- recognition of an exact expected fact
- statement splitting for multi-point responses
- lexical recovery of a fact missed by whole-answer semantic scoring
- preservation of the known paraphrase limitation in the current evaluator

Current checkpoint:

```text
4 tests passed
```

## Design Decisions

### Separate the system from the evaluator

The AI agent does not grade itself.

The project separates:

```text
grant_agent.py
→ system under test

run_evaluation.py
→ benchmark execution

score_evaluation.py
→ automated evaluator

generate_evaluation_report.py
→ reporting
```

This makes the evaluation logic easier to inspect and change independently.

### Preserve raw outputs

Raw agent responses are stored before scoring.

Changing the evaluator therefore does not require rerunning the agent.

This also enables controlled comparisons between evaluator versions using exactly the same AI responses.

### Transparent thresholds

The current evaluator uses explicit thresholds rather than hidden scoring rules:

```text
Lexical threshold: 0.60
Semantic threshold: 0.45
```

These thresholds are visible and configurable.

They should not be interpreted as universal standards.

### Human review remains necessary

Automated evaluation can produce false positives and false negatives.

The remaining Q09 false negative is intentionally documented rather than hidden.

## Technology

Current prototype:

- Python
- Google Gemini API
- sentence-transformers
- local sentence embeddings
- semantic similarity
- hybrid lexical + semantic evaluation
- JSON benchmark datasets
- structured evaluation outputs
- Markdown reporting
- python-dotenv
- pytest

## Limitations

This is an exploratory evaluation prototype rather than a production AI testing platform.

Current limitations include:

- the benchmark contains 12 questions
- the source procedure is fictional and controlled
- expected facts are manually authored
- lexical and semantic similarity are proxies for factual correctness
- similarity thresholds may produce false positives or false negatives
- semantic equivalence is not always captured reliably
- hallucination testing currently uses deliberately designed benchmark questions
- the evaluator does not yet independently detect every unsupported claim in an answer
- model behaviour may vary across repeated API calls
- the benchmark currently tests one document-grounded agent
- human review remains necessary when interpreting evaluation results

## Future Development

Potential next iterations include:

- repeated-run consistency testing
- paraphrased versions of benchmark questions
- adversarial and ambiguous prompts
- automatic unsupported-claim detection
- LLM-as-a-judge comparison against the transparent evaluator
- human-labelled evaluator calibration data
- precision and recall analysis for evaluator decisions
- larger benchmark datasets
- performance breakdown by question type
- latency and cost tracking
- multiple models or agents under the same benchmark
- regression testing between model versions
- configurable evaluation thresholds
- lightweight dashboard or web interface

## Status

**V1 — functional AI agent evaluation prototype**

The project demonstrates an end-to-end evaluation workflow:

```text
define benchmark
→ run AI agent
→ preserve raw responses
→ evaluate expected-fact coverage
→ test hallucination resistance
→ inspect evaluator failures
→ generate structured report
```

The project also demonstrates that evaluating AI systems is itself an engineering problem.

Testing exposed limitations in both lexical matching and naive semantic similarity, leading to a hybrid evaluation approach while retaining a known false negative for transparent human review.