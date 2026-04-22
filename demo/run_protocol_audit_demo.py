import json
from urllib.error import HTTPError, URLError

from src.agents.protocol_audit_agent import ProtocolAuditAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.schemas.patient import PatientProfile


def main() -> None:
    patient = PatientProfile(
        patient_id="patient_003",
        age=70,
        sex="female",
        conditions=["heart_failure", "chronic_kidney_disease"],
        medications=["furosemide", "spironolactone"],
        labs={"egfr": 42.0},
    )

    retrieval_agent = RetrievalAgent()
    protocol_agent = ProtocolAuditAgent()

    try:
        evidence_pack = retrieval_agent.retrieve_evidence(
            patient=patient,
            protocol_focus="heart failure reduced ejection fraction renal constraints",
            fetch_query="heart failure",
            top_k=3,
        )
    except (HTTPError, URLError, TimeoutError) as exc:  # pragma: no cover - network path
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Failed to retrieve protocol evidence",
                    "details": str(exc),
                },
                indent=2,
            )
        )
        return

    decision = protocol_agent.audit(patient=patient, evidence_pack=evidence_pack)
    output = {
        "query": evidence_pack.query,
        "citations_count": len(evidence_pack.citations),
        "decision": decision.to_dict(),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
