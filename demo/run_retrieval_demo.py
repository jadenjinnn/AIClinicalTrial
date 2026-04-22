import json

from src.retrieval.ctgov_client import ClinicalTrialsGovClient
from src.retrieval.indexer import InMemoryTrialIndexer


def main() -> None:
    query = "heart failure reduced ejection fraction chronic kidney disease"
    client = ClinicalTrialsGovClient()

    try:
        trials = client.search_studies(query="heart failure", page_size=10, max_pages=1)
    except Exception as exc:  # pragma: no cover - network-dependent path
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Unable to fetch from ClinicalTrials.gov API",
                    "details": str(exc),
                },
                indent=2,
            )
        )
        return

    indexer = InMemoryTrialIndexer()
    indexer.add_trials(trials)
    ranked = indexer.search(query=query, top_k=3)

    payload = []
    for item in ranked:
        payload.append(
            {
                "nct_id": item.trial.nct_id,
                "title": item.trial.title,
                "score": round(item.score, 4),
                "conditions": item.trial.conditions[:5],
                "inclusion_samples": item.trial.parsed_criteria.inclusion_criteria[:3],
                "exclusion_samples": item.trial.parsed_criteria.exclusion_criteria[:3],
            }
        )

    print(json.dumps({"query": query, "results": payload}, indent=2))


if __name__ == "__main__":
    main()
