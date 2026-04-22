from src.schemas.decision import EligibilityDecision, EvidenceItem
from src.schemas.patient import PatientProfile
from src.schemas.trial import TrialCriteria


def _has_condition(patient: PatientProfile, condition: str) -> bool:
    return condition.lower() in patient.conditions


def _has_medication(patient: PatientProfile, medication: str) -> bool:
    return medication.lower() in patient.medications


def evaluate_patient_against_trial(
    patient: PatientProfile, trial: TrialCriteria
) -> EligibilityDecision:
    passes: list[str] = []
    violations: list[str] = []
    missing_data: list[str] = []
    evidence: list[EvidenceItem] = []

    if trial.min_age is not None:
        if patient.age >= trial.min_age:
            passes.append(f"age >= {trial.min_age}")
        else:
            violations.append(f"age < {trial.min_age}")
        evidence.append(
            EvidenceItem(
                source="patient_profile",
                field="age",
                value=str(patient.age),
                rationale=f"Compared against minimum age {trial.min_age}",
            )
        )

    if trial.max_age is not None:
        if patient.age <= trial.max_age:
            passes.append(f"age <= {trial.max_age}")
        else:
            violations.append(f"age > {trial.max_age}")
        evidence.append(
            EvidenceItem(
                source="patient_profile",
                field="age",
                value=str(patient.age),
                rationale=f"Compared against maximum age {trial.max_age}",
            )
        )

    for condition in trial.required_conditions:
        if _has_condition(patient, condition):
            passes.append(f"required condition present: {condition}")
        else:
            violations.append(f"missing required condition: {condition}")
        evidence.append(
            EvidenceItem(
                source="patient_profile",
                field="conditions",
                value=condition,
                rationale="Required condition check",
            )
        )

    for condition in trial.excluded_conditions:
        if _has_condition(patient, condition):
            violations.append(f"excluded condition present: {condition}")
        else:
            passes.append(f"excluded condition absent: {condition}")
        evidence.append(
            EvidenceItem(
                source="patient_profile",
                field="conditions",
                value=condition,
                rationale="Exclusion condition check",
            )
        )

    for medication in trial.excluded_medications:
        if _has_medication(patient, medication):
            violations.append(f"excluded medication present: {medication}")
        else:
            passes.append(f"excluded medication absent: {medication}")
        evidence.append(
            EvidenceItem(
                source="patient_profile",
                field="medications",
                value=medication,
                rationale="Exclusion medication check",
            )
        )

    for lab, threshold in trial.required_labs_min.items():
        if lab not in patient.labs:
            missing_data.append(f"missing lab: {lab}")
        elif patient.labs[lab] >= threshold:
            passes.append(f"{lab} >= {threshold}")
        else:
            violations.append(f"{lab} < {threshold}")
        evidence.append(
            EvidenceItem(
                source="patient_profile",
                field=f"labs.{lab}",
                value=str(patient.labs.get(lab, "NA")),
                rationale=f"Minimum lab threshold check: {threshold}",
            )
        )

    for lab, threshold in trial.required_labs_max.items():
        if lab not in patient.labs:
            missing_data.append(f"missing lab: {lab}")
        elif patient.labs[lab] <= threshold:
            passes.append(f"{lab} <= {threshold}")
        else:
            violations.append(f"{lab} > {threshold}")
        evidence.append(
            EvidenceItem(
                source="patient_profile",
                field=f"labs.{lab}",
                value=str(patient.labs.get(lab, "NA")),
                rationale=f"Maximum lab threshold check: {threshold}",
            )
        )

    eligible = len(violations) == 0
    confidence = 0.95 if eligible else 0.8
    if missing_data:
        confidence -= 0.2
    confidence = max(0.0, min(1.0, confidence))

    return EligibilityDecision(
        patient_id=patient.patient_id,
        trial_id=trial.trial_id,
        eligible=eligible,
        confidence=confidence,
        passes=passes,
        violations=violations,
        missing_data=missing_data,
        evidence=evidence,
    )
