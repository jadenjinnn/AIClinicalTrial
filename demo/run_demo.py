import json

from src.engine.rules import evaluate_patient_against_trial
from src.schemas.patient import PatientProfile
from src.schemas.trial import TrialCriteria


def main() -> None:
    patient = PatientProfile(
        patient_id="patient_001",
        age=62,
        sex="male",
        conditions=["heart_failure", "hypertension"],
        medications=["aspirin"],
        labs={"egfr": 58.0, "hemoglobin": 13.1},
    )

    trial = TrialCriteria(
        trial_id="NCT-DEMO-001",
        title="Heart Failure Therapy Pilot",
        min_age=18,
        max_age=75,
        required_conditions=["heart_failure"],
        excluded_conditions=["active_cancer"],
        excluded_medications=["warfarin"],
        required_labs_min={"egfr": 45.0},
        required_labs_max={"hemoglobin": 16.0},
    )

    decision = evaluate_patient_against_trial(patient, trial)
    print(json.dumps(decision.to_dict(), indent=2))


if __name__ == "__main__":
    main()
