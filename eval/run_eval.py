import json
from pathlib import Path

from src.engine.rules import evaluate_patient_against_trial
from src.schemas.patient import PatientProfile
from src.schemas.trial import TrialCriteria


def main() -> None:
    cases_path = Path("eval/labeled_cases.json")
    cases = json.loads(cases_path.read_text(encoding="utf-8"))

    tp = tn = fp = fn = 0
    by_case: list[dict] = []

    for case in cases:
        patient = PatientProfile(**case["patient"])
        trial = TrialCriteria(**case["trial"])
        decision = evaluate_patient_against_trial(patient, trial)
        expected = bool(case["expected_eligible"])
        predicted = bool(decision.eligible)

        if expected and predicted:
            tp += 1
        elif (not expected) and (not predicted):
            tn += 1
        elif (not expected) and predicted:
            fp += 1
        else:
            fn += 1

        by_case.append(
            {
                "case_id": case["case_id"],
                "expected": expected,
                "predicted": predicted,
                "violations": decision.violations,
                "missing_data": decision.missing_data,
            }
        )

    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    summary = {
        "total_cases": total,
        "confusion_matrix": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "cases": by_case,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
