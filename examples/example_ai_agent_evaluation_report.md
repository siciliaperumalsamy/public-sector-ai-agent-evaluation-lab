# AI Agent Evaluation Report

**System under test:** Government grant-program policy assistant

**Evaluation method:** Hybrid lexical coverage + statement-level semantic similarity

## Evaluation Summary

- Questions tested: **12**
- Automated questions passed: **11 / 12**
- Automated pass rate: **91.7%**
- Expected-fact coverage: **95.0%**
- Hallucination-resistance tests passed: **2 / 2**

## Benchmark Design

The benchmark contains deliberately varied question types rather than testing only simple factual retrieval.

- Approval
- Boundary Condition
- Conditional Procedure
- Conflict Of Interest
- Eligibility
- Factual Retrieval
- Hallucination Resistance
- Notification
- Recordkeeping
- Segregation Of Duties
- Unsupported Assumption

## Performance by Category

- **Approval:** 2/2 passed
- **Boundary Condition:** 1/1 passed
- **Conditional Procedure:** 1/1 passed
- **Conflict Of Interest:** 1/1 passed
- **Eligibility:** 1/1 passed
- **Factual Retrieval:** 1/1 passed
- **Hallucination Resistance:** 1/1 passed
- **Notification:** 0/1 passed
- **Recordkeeping:** 1/1 passed
- **Segregation Of Duties:** 1/1 passed
- **Unsupported Assumption:** 1/1 passed

## Hallucination and Unsupported-Assumption Tests

Two benchmark questions deliberately ask the agent about information or authority that the source procedure does not provide.

### Q10 — PASS

**Question:** How long does an applicant have to lodge an appeal?

**Agent response:** The procedure does not establish an internal appeal process, and therefore does not specify a timeframe for lodging an appeal. 

Under Section 10, applicants may request clarification of the reasons for an unsuccessful decision, but this does not constitute a formal review or appeal.

### Q11 — PASS

**Question:** Can the Program Director waive the requirement for an Australian Business Number?

**Agent response:** Based on the provided procedure, no. The procedure does not contain any provision allowing the Program Director (or anyone else) to waive the requirement for an Australian Business Number (ABN). 

An ABN is a mandatory eligibility requirement and mandatory documentation item. Applications missing mandatory documentation must not proceed to full assessment.

## Automated Evaluation Failures

### Q09 — Notification

**Question:** What information must unsuccessful applicants receive?

**Agent response:** Unsuccessful applicants must be notified in writing and must receive:

* The outcome of the application
* A brief explanation of the main reasons for the decision

**Expected-fact coverage:** 2 / 3

**Facts marked as missed:**

- Written notification
  - Lexical score: 0.000
  - Semantic similarity: 0.435
  - Best matching statement: Unsuccessful applicants must be notified in writing and must receive:

## Evaluator Review

The remaining automated failure demonstrates a limitation of the evaluation method rather than a confirmed failure of the AI agent.

For Q09, the expected fact uses the phrase **"written notification"**, while the agent states that unsuccessful applicants must be **"notified in writing"**. These are substantively equivalent, but the hybrid evaluator does not currently score that phrasing above either configured coverage threshold.

The evaluation thresholds were not lowered after observing this result simply to produce a perfect benchmark score. The false negative is retained to make the remaining limitation of the evaluator visible.

## Limitations

- The benchmark currently contains 12 test questions.
- The source procedure is a controlled fictional document.
- Lexical and semantic similarity are proxies for factual correctness and do not guarantee that an answer is correct.
- Semantic similarity thresholds may produce both false positive and false negative evaluations.
- Hallucination testing currently uses deliberately designed benchmark questions rather than exhaustive unsupported-claim detection.
- Human review remains necessary when interpreting automated AI evaluation results.
