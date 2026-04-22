import json
from pathlib import Path
from typing import Any

from src.engine.rules import evaluate_patient_against_trial
from src.schemas.decision import EligibilityDecision
from src.schemas.patient import PatientProfile
from src.schemas.trial import TrialCriteria


def _resolve_expected_label(case: dict[str, Any]) -> tuple[bool, str]:
    if case.get("human_review_label") is not None:
        return bool(case["human_review_label"]), "human_review_label"
    if case.get("llm_assisted_label") is not None:
        return bool(case["llm_assisted_label"]), "llm_assisted_label"
    if case.get("rule_based_label") is not None:
        return bool(case["rule_based_label"]), "rule_based_label"
    return bool(case["expected_eligible"]), "expected_eligible"


def _derive_error_tags(decision: EligibilityDecision) -> list[str]:
    if decision.error_tags:
        return decision.error_tags

    tags: set[str] = set()
    violation_blob = " ".join(decision.violations).lower()
    missing_blob = " ".join(decision.missing_data).lower()
    pass_blob = " ".join(decision.passes).lower()

    if "no retrieved citations" in violation_blob or "no retrieved citations" in missing_blob:
        tags.add("retrieval_miss")
    if "no explicit age criterion" in violation_blob or "no explicit age criterion" in missing_blob:
        tags.add("criteria_parse_error")
    if decision.missing_data:
        tags.add("missing_data")
    if "age fits inclusion range" in pass_blob and "age fails inclusion range" in violation_blob:
        tags.add("reasoning_conflict")

    return sorted(tags)


def _metrics(tp: int, tn: int, fp: int, fn: int) -> dict[str, float]:
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "total_cases": total,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def main() -> None:
    cases_path = Path("eval/labeled_cases.json")
    cases = json.loads(cases_path.read_text(encoding="utf-8"))

    tp = tn = fp = fn = 0
    gold_tp = gold_tn = gold_fp = gold_fn = 0
    tier_counts = {"rule_based_label": 0, "llm_assisted_label": 0, "human_review_label": 0}
    error_taxonomy_counts = {
        "retrieval_miss": 0,
        "criteria_parse_error": 0,
        "reasoning_conflict": 0,
        "missing_data": 0,
    }
    by_case: list[dict] = []

    for case in cases:
        patient = PatientProfile(**case["patient"])
        trial = TrialCriteria(**case["trial"])
        decision = evaluate_patient_against_trial(patient, trial)
        expected, label_tier = _resolve_expected_label(case)
        predicted = bool(decision.eligible)
        error_tags = _derive_error_tags(decision)
        if label_tier in tier_counts:
            tier_counts[label_tier] += 1

        if expected and predicted:
            tp += 1
        elif (not expected) and (not predicted):
            tn += 1
        elif (not expected) and predicted:
            fp += 1
        else:
            fn += 1

        is_gold_case = case.get("human_review_label") is not None
        if is_gold_case:
            if expected and predicted:
                gold_tp += 1
            elif (not expected) and (not predicted):
                gold_tn += 1
            elif (not expected) and predicted:
                gold_fp += 1
            else:
                gold_fn += 1

        for tag in error_tags:
            if tag in error_taxonomy_counts:
                error_taxonomy_counts[tag] += 1

        by_case.append(
            {
                "case_id": case["case_id"],
                "label_tier": label_tier,
                "is_gold_case": is_gold_case,
                "expected": expected,
                "predicted": predicted,
                "violations": decision.violations,
                "missing_data": decision.missing_data,
                "error_tags": error_tags,
            }
        )

    summary = {
        **_metrics(tp, tn, fp, fn),
        "confusion_matrix": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "gold_subset_metrics": {
            **_metrics(gold_tp, gold_tn, gold_fp, gold_fn),
            "confusion_matrix": {
                "tp": gold_tp,
                "tn": gold_tn,
                "fp": gold_fp,
                "fn": gold_fn,
            },
        },
        "label_tier_counts": tier_counts,
        "error_taxonomy_counts": error_taxonomy_counts,
        "cases": by_case,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
