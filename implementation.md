# Phase 72 — Chain of Thought vs Direct Answer on SAR Question

**Version:** 1.1 | **Tier:** Standard | **Date:** 2026-03-27

## Goal
Compare chain-of-thought (CoT) prompting vs direct-answer prompting on a multi-step SAR reasoning question.

CLI: `python main.py --input data/compounds.csv`

Outputs: cot_comparison.json, cot_report.txt

## Logic
- Pose a multi-step SAR question: "Which scaffold family should we prioritize?"
- Direct prompt: "Answer concisely"
- CoT prompt: "Think step by step: 1) mean pIC50 per family, 2) best/worst, 3) consistency, 4) recommend with evidence"
- Score on 4 objective criteria: has_pic50_values, compares_scaffolds, has_recommendation, has_evidence

## Key Concepts
- CoT: explicit step-by-step reasoning instructions
- Quality rubric: 4 binary criteria scored by keyword/pattern matching
- Token cost comparison: CoT typically more verbose but more thorough

## Verification Checklist
- [x] Both prompts produce coherent responses
- [x] CoT response shows explicit step-by-step reasoning
- [x] Quality rubric applied objectively (keyword/pattern matching, not subjective)
- [x] Both responses recommend indole scaffold (correct answer)
- [x] Token cost difference measured (2.8× more for CoT)

## Risks (resolved)
- Subjective quality scoring — mitigated by using objective keyword/pattern matching rubric
- Modern models may CoT internally even without explicit prompting — confirmed (both scored 4/4)
- Small sample (1 question) limits generalizability — acknowledged; finding is directional

## Results
| Metric | Value |
|--------|-------|
| Direct quality | 4/4 |
| CoT quality | 4/4 |
| Direct tokens | 345 output |
| CoT tokens | 960 output (2.8× more) |
| Total tokens | in=1997 out=1305 |
| Est. cost | $0.0068 |

Key finding: Both achieved 4/4 quality on this task. CoT produced more structured output (tables, step-by-step analysis) at 2.8× token cost. For well-specified questions with clear data, Haiku performs well without CoT. CoT adds thoroughness at the cost of verbosity — useful for complex reasoning but not always necessary.
