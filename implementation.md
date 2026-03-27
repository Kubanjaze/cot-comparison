# Phase 72 — Chain of Thought vs Direct Answer on SAR Question

**Version:** 1.0 | **Tier:** Standard | **Date:** 2026-03-27

## Goal
Compare chain-of-thought (CoT) prompting vs direct-answer prompting on a multi-step SAR reasoning question. Measures whether explicit reasoning steps improve answer quality and accuracy.

CLI: `python main.py --input data/compounds.csv`

Outputs: cot_comparison.json, cot_report.txt

## Logic
- Pose a multi-step SAR question: "Which scaffold family should we prioritize for lead optimization, and why?"
- Direct prompt: "Answer this question concisely."
- CoT prompt: "Think step by step. First analyze each scaffold's potency. Then compare trends. Then recommend."
- Score responses on: (1) mentions specific pIC50 values, (2) compares multiple scaffolds, (3) gives clear recommendation, (4) cites evidence for recommendation
- Report: quality scores, response lengths, token usage comparison

## Key Concepts
- Chain-of-thought: explicitly asking model to reason step-by-step
- Quality scoring: rubric-based evaluation (4 criteria, 0-1 each)
- Direct vs CoT may differ more on complex multi-step reasoning than simple lookups
- Token cost: CoT typically uses more output tokens

## Verification Checklist
- [ ] Both prompts produce coherent responses
- [ ] CoT response shows explicit reasoning steps
- [ ] Quality rubric applied to both responses
- [ ] 2 API calls total

## Risks
- Subjective quality scoring — rubric must be objective (keyword/pattern matching)
- Modern models may CoT internally even without explicit prompting
