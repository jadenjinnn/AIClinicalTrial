import json
from urllib.error import HTTPError, URLError

from src.agents.retrieval_agent import RetrievalAgent
from src.schemas.patient import PatientProfile


def main() -> None:
    patient = PatientProfile(
        patient_id="patient_002",
        age=70,
        sex="female",
        conditions=["heart_failure", "chronic_kidney_disease"],
        medications=["furosemide", "spironolactone"],
        labs={"egfr": 42.0},
    )

    agent = RetrievalAgent()
    try:
        evidence_pack = agent.retrieve_evidence(
            patient=patient,
            protocol_focus="reduced ejection fraction renal function constraints",
            fetch_query="heart failure",
            top_k=3,
        )
    except (HTTPError, URLError, TimeoutError) as exc:  # pragma: no cover - network path
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "RetrievalAgent failed to fetch evidence",
                    "details": str(exc),
                },
                indent=2,
            )
        )
        return

    print(json.dumps(evidence_pack.to_dict(), indent=2))


if __name__ == "__main__":
    main()
