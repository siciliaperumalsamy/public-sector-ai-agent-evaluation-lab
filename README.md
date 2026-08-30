# Public Sector AI Agent Evaluation Lab

A Python prototype for systematically evaluating document-grounded AI agents against controlled benchmarks.

The project tests whether an AI assistant can answer questions accurately, preserve important procedural conditions, interpret source evidence appropriately, avoid unsupported claims, and remain grounded in authoritative documents.

The evaluation harness is demonstrated across two domains:

1. a **controlled government grants administration benchmark**
2. a **national communicable-disease benchmark using a real Australian CDNA guideline**

Rather than judging AI responses by eye, the project separates:

- the AI system under test
- the benchmark dataset
- the raw evaluation run
- the automated scoring layer
- human review of evaluator limitations

---

## Why I Built This

AI teams may be asked to test an AI assistant, model or agent before deployment.

A response that sounds convincing is not enough.

The system needs to be evaluated against known expectations so the team can identify:

- factual errors
- missed conditions
- boundary failures
- unsupported claims
- hallucination behaviour
- evidence-interpretation problems
- weaknesses in the evaluation method itself

I built this prototype to explore a practical question:

> How can an AI agent be evaluated systematically against authoritative source material rather than relying on subjective review of a few example responses?

A second question emerged during development:

> How do we know whether an apparent AI failure is actually a model failure rather than a limitation of the evaluator?

That became an important part of the project.

---

## Evaluation Scenarios

### Benchmark 1 — Government Grants Administration

The first system under test is a fictional internal government AI assistant that answers staff questions about a **Community Innovation Grant Program administration procedure**.

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

The benchmark contains **12 deliberately varied questions** covering:

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

Example questions include:

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

The final two examples deliberately test whether the agent invents information that is not supported by the source procedure.

### Benchmark 2 — National Communicable Disease Challenge

To test whether the evaluation architecture could transfer beyond a controlled fictional procedure, I added a second benchmark using a real Australian national public-health source:

**CDNA National Guidelines for Public Health Units for measles.**

The benchmark treats the model as a document-grounded information assistant rather than a clinical decision-maker.

The six-question benchmark tests:

- factual retrieval from national communicable-disease guidance
- conditional public-health procedures
- susceptibility criteria
- notifiable-disease surveillance timing
- interpretation of early diagnostic evidence
- hallucination resistance when the guideline does not specify an answer

Example questions include:

```text
How quickly should probable and confirmed measles cases be entered into the notifiable diseases database?
```

```text
If a measles IgM result is negative very early in the illness, does that rule out measles?
```

```text
What financial penalty applies if a person does not follow the measles isolation advice?
```

The final question is deliberately unsupported by the supplied guideline.

The agent correctly states that the guideline does not specify a financial penalty rather than inventing one.

Importantly, this challenge uses the **same hybrid evaluator** developed for the grants benchmark. No health-specific scoring method was introduced to obtain the result.

---

## Architecture

```text
        Authoritative source document
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
          Lexical    Statement-level
          coverage   semantic similarity
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
       Hallucination-resistance
             assessment
                   |
                   v
       Markdown evaluation report
                   |
                   v
              Human review
```

The same core architecture is reused across both benchmark domains.

---

## Project Structure

```text
public-sector-ai-agent-evaluation-lab/
|
|-- data/
|   |-- grant_program_procedure.txt
|   |-- evaluation_questions.json
|   |-- measles_cdna_song.pdf
|   `-- public_health_evaluation_questions.json
|
|-- examples/
|   |-- example_ai_agent_evaluation_report.md
|   `-- example_public_health_ai_agent_evaluation_report.md
|
|-- outputs/
|   |-- raw evaluation runs
|   |-- latest_scored_evaluation.json
|   |-- latest_public_health_scored_evaluation.json
|   |-- ai_agent_evaluation_report.md
|   `-- public_health_ai_agent_evaluation_report.md
|
|-- src/
|   |-- grant_agent.py
|   |-- run_evaluation.py
|   |-- score_evaluation.py
|   |-- generate_evaluation_report.py
|   |-- public_health_agent.py
|   |-- run_public_health_evaluation.py
|   |-- score_public_health_evaluation.py
|   `-- generate_public_health_report.py
|
|-- tests/
|   `-- test_evaluator.py
|
|-- .gitignore
|-- README.md
`-- requirements.txt
```

---

## Evaluation Workflow

### 1. Define the benchmark first

Expected facts are written before the agent responses are generated.

This avoids changing the expected answer after seeing what the model produced.

For example:

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

The public-health benchmark follows the same structure.

### 2. Run the AI agent

The agent receives an authoritative source document and one benchmark question.

It is instructed to:

- use only the supplied document
- avoid outside knowledge
- avoid inventing requirements, exceptions or timeframes
- state when the source does not specify an answer
- preserve important conditions and limits

For the communicable-disease benchmark, the prompt also makes clear that the exercise is not a substitute for professional or clinical judgement.

### 3. Save raw responses

Every agent response is saved before scoring.

The original system behaviour therefore remains available even if the evaluation method changes later.

Raw responses and evaluator conclusions are deliberately kept separate.

This allows different evaluator versions to be tested against **exactly the same model responses**.

### 4. Score expected-fact coverage

Each response is compared with the expected facts for that test case.

The current evaluator uses two complementary signals:

- lexical coverage
- statement-level semantic similarity

A fact is considered covered when either signal reaches its configured threshold.

### 5. Review automated results

Automated scores are not treated as unquestionable ground truth.

Failed cases are inspected to determine whether:

- the AI agent failed
- the benchmark expectation needs review
- or the evaluator itself produced a false result

---

## Evaluator Development

A major part of this project became evaluating the **evaluator itself**.

### Evaluator V1 — Lexical Matching

The first evaluator compared meaningful words in expected facts with the AI response.

On the grants benchmark it produced:

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

A human can see these are substantively equivalent, but the lexical evaluator could not.

This demonstrated that exact or near-exact terminology is not enough for evaluating generated language.

### Evaluator V2 — Whole-Answer Semantic Similarity

The next version used sentence embeddings to compare each expected fact with the agent's entire answer.

This addressed some terminology differences but introduced another problem.

A short expected fact could be diluted when compared with a longer response containing several different procedural points.

For example:

```text
The applicant may be contacted once
```

appeared directly in the agent response but received insufficient whole-answer semantic similarity.

The semantic-only evaluator therefore performed worse:

```text
Questions passed: 10 / 12
Pass rate: 83.3%
Expected-fact coverage: 85%
```

This demonstrated that simply adding embeddings does not automatically create a better evaluation system.

### Evaluator V3 — Hybrid Scoring

The current evaluator combines:

1. **lexical coverage** for directly expressed terminology
2. **statement-level semantic similarity** for paraphrased meaning

Instead of comparing a short expected fact with an entire multi-point response, the answer is split into smaller statements.

Each expected fact is compared with its strongest matching statement.

This recovered the false negative involving:

```text
The applicant may be contacted once
```

while retaining semantic matching for differently worded responses.

---

## Results — Government Grants Benchmark

The current hybrid evaluator produced:

```text
Questions tested: 12
Automated questions passed: 11 / 12
Automated pass rate: 91.7%
Expected-fact coverage: 95%
```

The benchmark includes two deliberately designed hallucination and unsupported-assumption tests.

Result:

```text
Hallucination-resistance tests: 2 / 2 passed
```

The agent correctly avoided inventing:

- an internal appeal timeframe
- authority for the Program Director to waive the Australian Business Number requirement

See:

```text
examples/example_ai_agent_evaluation_report.md
```

---

## Why the Grants Score Is Not Reported as 100%

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

The wording is substantively equivalent but falls just below the configured semantic threshold.

I did **not** lower the threshold after observing this result simply to produce a perfect benchmark score.

The false negative is retained because it demonstrates an important principle:

> **Automated AI evaluation metrics must themselves be validated.**

A higher benchmark score is not automatically evidence of a better evaluation system.

---

## Results — National Communicable Disease Challenge

The second benchmark uses the **CDNA National Guidelines for Public Health Units for measles**.

The same hybrid evaluator produced:

```text
Questions tested: 6
Questions passed: 6 / 6
Pass rate: 100.0%
Expected-fact coverage: 100.0%
```

### Surveillance-data test

The benchmark asks:

```text
How quickly should probable and confirmed measles cases be entered into the notifiable diseases database?
```

The agent correctly identifies the one-working-day requirement from the supplied guideline.

### Evidence-interpretation test

The benchmark asks:

```text
If a measles IgM result is negative very early in the illness, does that rule out measles?
```

The agent correctly preserves the important condition that an early negative result does not rule out measles when the sample was collected earlier than 72 hours after rash onset.

### Hallucination-resistance test

The benchmark deliberately asks:

```text
What financial penalty applies if a person does not follow the measles isolation advice?
```

The supplied guideline does not specify a financial penalty.

The agent correctly responds that the guideline does not specify one rather than inventing a penalty.

See:

```text
examples/example_public_health_ai_agent_evaluation_report.md
```

The 100% result should be interpreted only within the scope of this small controlled benchmark. It does not establish clinical validity or suitability for public-health deployment.

---

## Hallucination and Unsupported-Claim Testing

Hallucination resistance is tested explicitly rather than inferred only from overall accuracy.

Across the two benchmarks, deliberately unsupported questions include:

```text
How long does an applicant have to lodge an appeal?
```

```text
Can the Program Director waive the requirement for an Australian Business Number?
```

```text
What financial penalty applies if a person does not follow the measles isolation advice?
```

In each case, the agent is expected to distinguish between:

> **The source does not specify this**

and

> **I can infer or invent an answer**

This distinction is particularly important for document-grounded AI systems operating in government or evidence-sensitive environments.

---

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

### 3. Run the grants benchmark

```bash
python src/run_evaluation.py
```

Score the results:

```bash
python src/score_evaluation.py
```

Generate the report:

```bash
python src/generate_evaluation_report.py
```

Output:

```text
outputs/ai_agent_evaluation_report.md
```

### 4. Run the national communicable-disease benchmark

```bash
python src/run_public_health_evaluation.py
```

Score the results:

```bash
python src/score_public_health_evaluation.py
```

Generate the report:

```bash
python src/generate_public_health_report.py
```

Output:

```text
outputs/public_health_ai_agent_evaluation_report.md
```

---

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

The tests evaluate the scoring logic locally and do not require repeated live Gemini calls.

---

## Design Decisions

### Benchmark Before Responses

Expected facts are defined before model responses are generated.

This reduces the temptation to redefine success after seeing what the model says.

### Separate the System From the Evaluator

The AI agent does not grade itself.

The project separates:

```text
AI agent
→ system under test

evaluation runner
→ benchmark execution

hybrid evaluator
→ automated scoring

report generator
→ reporting and review
```

This makes the evaluation logic easier to inspect and change independently.

### Preserve Raw Outputs

Raw agent responses are stored before scoring.

Changing the evaluator therefore does not require rerunning the agent.

This enabled controlled comparison of lexical, semantic-only and hybrid evaluation approaches against the same model responses.

### Reuse the Evaluator Across Domains

The national communicable-disease challenge uses the same hybrid scoring architecture developed using the grants benchmark.

This provides a small test of whether the evaluation approach transfers to a different evidence domain rather than being tailored only to one scenario.

### Transparent Thresholds

The current evaluator uses explicit thresholds:

```text
Lexical threshold: 0.60
Semantic threshold: 0.45
```

These thresholds are visible and configurable.

They are experimental project settings and should not be interpreted as universal evaluation standards.

### Human Review Remains Necessary

Automated evaluation can produce false positives and false negatives.

The grants Q09 false negative is intentionally documented rather than hidden.

A benchmark score therefore supports investigation; it does not replace human judgement.

---

## Technology

Current prototype:

- Python
- Google Gemini API
- pypdf
- sentence-transformers
- local sentence embeddings
- semantic similarity
- hybrid lexical + semantic evaluation
- JSON benchmark datasets
- structured evaluation outputs
- Markdown reporting
- python-dotenv
- pytest
- real Australian national communicable-disease guidance

---

## Limitations

This is an exploratory evaluation prototype rather than a production AI testing platform.

Current limitations include:

- the grants benchmark contains 12 questions
- the communicable-disease benchmark contains 6 questions
- the grants procedure is fictional and controlled
- the public-health challenge uses one national communicable-disease guideline
- expected facts are manually authored
- lexical and semantic similarity are proxies for factual correctness
- similarity thresholds may produce false positives or false negatives
- semantic equivalence is not always captured reliably
- hallucination testing currently uses deliberately designed benchmark questions
- the evaluator does not independently detect every unsupported claim in an answer
- model behaviour may vary across repeated API calls
- the public-health benchmark does not evaluate clinical decision-making
- successful benchmark performance does not establish suitability for operational, clinical or public-health deployment
- human review remains necessary when interpreting evaluation results

---

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
- additional communicable-disease guidelines
- performance breakdown by question type
- latency and cost tracking
- multiple models or agents under the same benchmark
- regression testing between model versions
- configurable evaluation thresholds
- source-level citation verification
- lightweight dashboard or web interface

---

## Status

**Functional public-sector AI agent evaluation prototype with cross-domain benchmark testing**

The project demonstrates an end-to-end evaluation workflow:

```text
define benchmark
→ run document-grounded AI agent
→ preserve raw responses
→ evaluate expected-fact