import re

from src.schemas.decision import EligibilityDecision, EvidenceItem
from src.schemas.evidence import RetrievalEvidencePack
from src.schemas.patient import PatientProfile


class ProtocolAuditAgent:
    def audit(
        self,
        patient: PatientProfile,
        evidence_pack: RetrievalEvidencePack,
    ) -> EligibilityDecision:
        passes: list[str] = []
        violations: list[str] = []
        missing_data: list[str] = []
        error_tags: set[str] = set()
        justifications: list[str] = []
        evidence_items: list[EvidenceItem] = []

        primary_trial_id = self._select_primary_trial(evidence_pack)

        patient_terms = set(patient.conditions + patient.medications)
        age_checked = False

        for citation in evidence_pack.citations:
            snippet_lower = citation.snippet.lower()
            evidence_items.append(
                EvidenceItem(
                    source=citation.source,
                    field=f"{citation.section}_criteria",
                    value=citation.snippet,
                    rationale=f"{citation.trial_id} ({citation.trial_title}) score={citation.relevance_score}",
                )
            )

            has_patient_term = any(term in snippet_lower for term in patient_terms if term)
            if citation.section == "inclusion":
                if has_patient_term:
                    passes.append(f"matches inclusion snippet: {citation.snippet}")
                    justifications.append(
                        "Patient profile terms overlap with inclusion criteria evidence."
                    )
                age_result = self._check_age_criterion(patient.age, citation.snippet)
                if age_result is not None:
                    age_checked = True
                    if age_result:
                        passes.append(f"age fits inclusion range in snippet: {citation.snippet}")
                    else:
                        violations.append(f"age fails inclusion range in snippet: {citation.snippet}")
            elif citation.section == "exclusion":
                if has_patient_term:
                    violations.append(
                        f"profile overlaps exclusion snippet: {citation.snippet}"
                    )
                    justifications.append(
                        "Exclusion criteria snippet references patient condition/medication."
                    )
                if "renal insufficiency" in snippet_lower and "chronic_kidney_disease" in patient.conditions:
                    violations.append(
                        "renal insufficiency exclusion likely triggered by chronic_kidney_disease"
                    )
                    justifications.append(
                        "Renal-related exclusion text conflicts with patient CKD condition."
                    )

        if not evidence_pack.citations:
            missing_data.append("no retrieved citations available for audit")
            justifications.append("Cannot make robust decision without protocol evidence.")
            error_tags.add("retrieval_miss")

        if not age_checked:
            missing_data.append("no explicit age criterion detected in retrieved snippets")
            error_tags.add("criteria_parse_error")

        if missing_data:
            error_tags.add("missing_data")

        eligible = len(violations) == 0 and len(evidence_pack.citations) > 0
        confidence = 0.85 if eligible else 0.7
        if missing_data:
            confidence -= 0.2
        confidence = max(0.0, min(1.0, confidence))

        if eligible:
            justifications.append("No exclusion conflicts identified in retrieved protocol snippets.")
        else:
            justifications.append("At least one protocol conflict or evidence gap was detected.")

        if self._has_reasoning_conflict(passes, violations):
            error_tags.add("reasoning_conflict")

        return EligibilityDecision(
            patient_id=patient.patient_id,
            trial_id=primary_trial_id,
            eligible=eligible,
            confidence=confidence,
            passes=passes,
            violations=violations,
            missing_data=missing_data,
            error_tags=sorted(error_tags),
            justifications=justifications,
            evidence=evidence_items,
        )

    def _select_primary_trial(self, evidence_pack: RetrievalEvidencePack) -> str:
        if not evidence_pack.citations:
            return "unknown_trial"
        sorted_citations = sorted(
            evidence_pack.citations, key=lambda c: c.relevance_score, reverse=True
        )
        return sorted_citations[0].trial_id

    def _check_age_criterion(self, age: int, snippet: str) -> bool | None:
        lowered = snippet.lower()
        if "age" not in lowered and "years old" not in lowered:
            return None

        numbers = [int(value) for value in re.findall(r"\b(\d{1,3})\b", snippet)]
        if len(numbers) >= 2:
            low, high = min(numbers[0], numbers[1]), max(numbers[0], numbers[1])
            return low <= age <= high
        if len(numbers) == 1:
            threshold = numbers[0]
            if any(token in lowered for token in ["at least", ">=", "older than"]):
                return age >= threshold
            if any(token in lowered for token in ["at most", "<=", "younger than"]):
                return age <= threshold
        return None

    def _has_reasoning_conflict(self, passes: list[str], violations: list[str]) -> bool:
        age_pass = any(item.startswith("age fits inclusion range") for item in passes)
        age_violation = any(item.startswith("age fails inclusion range") for item in violations)
        return age_pass and age_violation
