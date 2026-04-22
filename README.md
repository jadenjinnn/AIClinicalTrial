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
- evaluation harness over labeled cases,
- ClinicalTrials.gov retrieval client + criteria parsing baseline,
- retrieval/protocol agents + one-command end-to-end pipeline demo.

## Project structure

- `src/schemas/patient.py` - patient profile contract
- `src/schemas/trial.py` - trial criteria contract
- `src/schemas/decision.py` - decision output contract
- `src/schemas/evidence.py` - retrieval citation and evidence pack contract
- `src/engine/rules.py` - deterministic eligibility evaluation
- `src/retrieval/ctgov_client.py` - ClinicalTrials.gov retrieval client
- `src/retrieval/criteria_parser.py` - inclusion/exclusion parser
- `src/retrieval/indexer.py` - lightweight in-memory relevance ranker
- `src/agents/retrieval_agent.py` - retrieval agent for citation-ready evidence
- `src/agents/protocol_audit_agent.py` - protocol audit agent for eligibility decisions
- `src/pipeline/audit_pipeline.py` - pipeline orchestration and CLI report formatting
- `demo/run_demo.py` - local demo entry point
- `demo/run_retrieval_demo.py` - retrieval + ranking demo
- `demo/run_retrieval_agent_demo.py` - retrieval agent evidence-pack demo
- `demo/run_protocol_audit_demo.py` - retrieval + protocol audit end-to-end demo
- `demo/run_pipeline_demo.py` - one-command orchestrated pipeline demo
- `demo/scenarios/patient_scenarios.json` - canned scenario pack for interviews
- `eval/labeled_cases.json` - starter labeled set
- `eval/run_eval.py` - baseline evaluator
- `docs/project-thesis.md` - positioning and product narrative
- `docs/evaluation-plan.md` - lean evaluation strategy

## Run locally

Requires Python 3.10+.

Quick scenario discovery:

```bash
python -m demo.run_pipeline_demo --list-scenarios
```

One-command end-to-end demo:

```bash
python -m demo.run_pipeline_demo --scenario-id hf_ckd_exclusion_risk
```

Evaluation harness:

```bash
python -m eval.run_eval
```

Additional module demos:

```bash
python -m demo.run_demo
python -m demo.run_retrieval_demo
python -m demo.run_retrieval_agent_demo
python -m demo.run_protocol_audit_demo
python -m demo.run_pipeline_demo --scenario-id hf_stable_candidate --output json
```

The retrieval and pipeline demos require internet access to call the ClinicalTrials.gov API.

## Known limitations

- Protocol matching uses heuristic text parsing and does not perform clinical-grade NLP normalization.
- Retrieved evidence can include imperfectly matched trials due to lightweight ranking.
- Decisions are for protocol-fit auditing only and are not enrollment outcomes or medical advice.

## Failure modes to expect

- `retrieval_miss`: no usable protocol snippets were retrieved.
- `criteria_parse_error`: snippets did not include parseable age/constraint structure.
- `reasoning_conflict`: mixed evidence yields contradictory pass/fail signals.
- `missing_data`: patient profile lacks fields needed for stronger conclusions.

## Near-term roadmap

1. Improve retrieval relevance with stronger ranking and trial filtering.
2. Add protocol contradiction handling beyond age/renal patterns.
3. Expand gold-labeled hard cases (target 15-25) and refresh metrics.
4. Produce polished demo video and architecture case study for interviews.
