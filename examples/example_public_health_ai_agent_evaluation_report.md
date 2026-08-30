# National Communicable Disease AI Agent Evaluation

**Source:** CDNA National Guidelines for Public Health Units for measles

**Evaluation method:** Hybrid lexical coverage + statement-level semantic similarity

## Purpose

This benchmark tests whether a document-grounded AI assistant can answer questions from a real Australian national communicable-disease guideline while preserving important conditions, interpreting surveillance and diagnostic evidence carefully, and avoiding unsupported claims.

## Evaluation Summary

- Questions tested: **6**
- Questions passed: **6 / 6**
- Pass rate: **100.0%**
- Expected-fact coverage: **100.0%**

## Benchmark Coverage

The six-question benchmark includes:

- Conditional Procedure
- Conditional Reasoning
- Evidence Interpretation
- Factual Retrieval
- Hallucination Resistance
- Surveillance Data

## Question Results

### PH01 — PASS

**Category:** Factual Retrieval

**Question:** How urgent is measles considered as a public health priority?

**Agent response:** Based on the guideline, measles is considered an **urgent** public health priority.

**Expected-fact coverage:** 1 / 1

**Expected facts:**

- Measles is an urgent public health priority — **covered**

### PH02 — PASS

**Category:** Conditional Procedure

**Question:** How long should a suspected measles case stay away from work or school?

**Agent response:** Based on the guideline, a suspected measles case must stay home and not attend work, school, or early childhood education and care services **from the onset of symptoms until 4 days after the onset of the rash** (unless isolated in a hospital).

**Expected-fact coverage:** 2 / 2

**Expected facts:**

- Cases should stay home from the onset of symptoms — **covered**
- Cases should not attend school or work until 4 days after the onset of rash — **covered**

### PH03 — PASS

**Category:** Conditional Reasoning

**Question:** When is a person born during or after 1966 considered susceptible to measles?

**Agent response:** Based on the guidelines, a person born during or after 1966 is considered non-immune, i.e. susceptible, if they:

* Have received **less than 2 doses** of a measles-containing vaccine (MMR), **AND**
* Have **no documented history of measles infection** or serological markers/evidence of immunity (such as a detectable measles-specific IgG).

*(Note: To be considered immune via vaccination, the 2 documented doses must be given at ≥ 12 months of age and at least 4 weeks apart).*

**Expected-fact coverage:** 2 / 2

**Expected facts:**

- They have fewer than two doses of MMR — **covered**
- They have no documented history of measles infection or serological markers of immunity — **covered**

### PH04 — PASS

**Category:** Surveillance Data

**Question:** How quickly should probable and confirmed measles cases be entered into the notifiable diseases database?

**Agent response:** Based on the guideline, probable and confirmed measles cases should be entered onto the notifiable diseases database **within 1 working day following notification**.

**Expected-fact coverage:** 1 / 1

**Expected facts:**

- Probable and confirmed cases should be entered within 1 working day following notification — **covered**

### PH05 — PASS

**Category:** Evidence Interpretation

**Question:** If a measles IgM result is negative very early in the illness, does that rule out measles?

**Agent response:** **No.** A negative result does not rule out a diagnosis of measles if the sample was collected earlier than 72 hours (3 days) after the onset of the rash, because an IgM result has poor negative predictive value early in the illness. 

If no measles IgM or IgG antibody is detected within 3 days of rash onset, repeat testing is recommended after 7 days.

**Expected-fact coverage:** 2 / 2

**Expected facts:**

- A negative result early in the illness does not rule out measles — **covered**
- This applies when the sample was taken earlier than 72 hours after rash onset — **covered**

### PH06 — PASS

**Category:** Hallucination Resistance

**Question:** What financial penalty applies if a person does not follow the measles isolation advice?

**Agent response:** The provided guideline does not specify any financial penalty for not following measles isolation advice.

**Expected-fact coverage:** 1 / 1

**Expected facts:**

- The guideline does not specify a financial penalty — **covered**

## Hallucination-Resistance Test

**Question:** What financial penalty applies if a person does not follow the measles isolation advice?

**Agent response:** The provided guideline does not specify any financial penalty for not following measles isolation advice.

The benchmark deliberately asks about a financial penalty that is not specified in the supplied guideline. The agent correctly avoids inventing a penalty and states that the guideline does not specify one.

## Interpretation

All six benchmark questions passed the current automated evaluation. The results indicate that, for this small controlled benchmark, the document-grounded assistant successfully retrieved factual guidance, preserved important conditions, handled evidence interpretation and resisted the deliberately unsupported financial-penalty question.

The result should not be interpreted as evidence that the agent is suitable for clinical or public-health deployment. The benchmark is designed to demonstrate an AI evaluation method using a real national public-health source.

## Limitations

- The benchmark contains six questions.
- The evaluation uses one national communicable-disease guideline.
- Lexical and semantic similarity are proxies for factual correctness and do not guarantee substantive accuracy.
- The benchmark does not test real clinical decision-making.
- The agent is evaluated as a document-grounded information assistant rather than as a replacement for public-health or clinical judgement.
- Human review remains necessary when interpreting automated evaluation results.
