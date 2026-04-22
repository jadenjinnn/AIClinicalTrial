from src.retrieval.ctgov_client import ClinicalTrialsGovClient
from src.retrieval.indexer import InMemoryTrialIndexer
from src.schemas.evidence import Citation, RetrievalEvidencePack
from src.schemas.patient import PatientProfile


class RetrievalAgent:
    def __init__(self, client: ClinicalTrialsGovClient | None = None) -> None:
        self.client = client or ClinicalTrialsGovClient()

    def build_query(self, patient: PatientProfile, protocol_focus: str = "") -> str:
        condition_text = " ".join(patient.conditions[:5])
        medication_text = " ".join(patient.medications[:3])
        focus = protocol_focus.strip()
        parts = [condition_text, medication_text, focus]
        query = " ".join(part for part in parts if part).strip()
        return query or "clinical trial eligibility"

    def retrieve_evidence(
        self,
        patient: PatientProfile,
        protocol_focus: str = "",
        fetch_query: str = "heart failure",
        top_k: int = 3,
    ) -> RetrievalEvidencePack:
        query = self.build_query(patient=patient, protocol_focus=protocol_focus)
        trials = self.client.search_studies(query=fetch_query, page_size=10, max_pages=1)

        indexer = InMemoryTrialIndexer()
        indexer.add_trials(trials)
        ranked_trials = indexer.search(query=query, top_k=top_k)

        citations: list[Citation] = []
        for ranked in ranked_trials:
            trial = ranked.trial
            inclusion = trial.parsed_criteria.inclusion_criteria[:2]
            exclusion = trial.parsed_criteria.exclusion_criteria[:2]

            for snippet in inclusion:
                citations.append(
                    Citation(
                        source="clinicaltrials.gov",
                        trial_id=trial.nct_id,
                        trial_title=trial.title,
                        section="inclusion",
                        snippet=snippet,
                        relevance_score=round(ranked.score, 4),
                    )
                )

            for snippet in exclusion:
                citations.append(
                    Citation(
                        source="clinicaltrials.gov",
                        trial_id=trial.nct_id,
                        trial_title=trial.title,
                        section="exclusion",
                        snippet=snippet,
                        relevance_score=round(ranked.score, 4),
                    )
                )

        return RetrievalEvidencePack(query=query, citations=citations)
