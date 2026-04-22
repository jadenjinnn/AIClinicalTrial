# TrialMatch Audit

`TrialMatch Audit` is a lean applied-AI biotech project that evaluates whether a patient profile appears eligible for a clinical trial protocol using:

- deterministic inclusion/exclusion rule checks (baseline),
- traceable evidence and violation reporting,
- a structure that is ready for retrieval + LLM agents in later iterations.

## Why this exists

This project is optimized for interview signal:
- reproducible decision logic,
- explicit failure modes,
- auditable outputs (not opaque chat responses).

## Current scope (Day 1-2)

- strict schema contracts for patient, trial criteria, and decisions,
- deterministic rule engine,
- demo script for a single decision trace,
- evaluation harness over labeled cases.

## Project structure

- `src/schemas/patient.py` - patient profile contract
- `src/schemas/trial.py` - trial criteria contract
- `src/schemas/decision.py` - decision output contract
- `src/engine/rules.py` - deterministic eligibility evaluation
- `demo/run_demo.py` - local demo entry point
- `eval/labeled_cases.json` - starter labeled set
- `eval/run_eval.py` - baseline evaluator
- `docs/project-thesis.md` - positioning and product narrative
- `docs/evaluation-plan.md` - lean evaluation strategy

## Run locally

Requires Python 3.10+.

```bash
python -m demo.run_demo
python -m eval.run_eval
```

## Near-term roadmap

1. Add ClinicalTrials.gov retrieval and criterion parsing.
2. Add citation-aware evidence packaging.
3. Add retrieval/protocol agents with JSON contracts.
4. Add weak-label generation + small gold set adjudication.
