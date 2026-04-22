from dataclasses import dataclass, field
import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from src.retrieval.criteria_parser import ParsedEligibilityCriteria, parse_eligibility_criteria


BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


@dataclass
class RetrievedTrial:
    nct_id: str
    title: str
    conditions: list[str] = field(default_factory=list)
    criteria_text: str = ""
    parsed_criteria: ParsedEligibilityCriteria = field(default_factory=ParsedEligibilityCriteria)


class ClinicalTrialsGovClient:
    def __init__(self, base_url: str = BASE_URL, timeout_seconds: int = 20):
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    def search_studies(
        self,
        query: str,
        page_size: int = 10,
        max_pages: int = 1,
    ) -> list[RetrievedTrial]:
        if not query.strip():
            raise ValueError("query must be non-empty")
        if page_size < 1:
            raise ValueError("page_size must be >= 1")
        if max_pages < 1:
            raise ValueError("max_pages must be >= 1")

        all_trials: list[RetrievedTrial] = []
        page_token: str | None = None

        for _ in range(max_pages):
            payload = self._fetch_page(query=query, page_size=page_size, page_token=page_token)
            studies = payload.get("studies", [])
            for study in studies:
                all_trials.append(self._to_trial(study))

            page_token = payload.get("nextPageToken")
            if not page_token:
                break

        return all_trials

    def _fetch_page(
        self,
        query: str,
        page_size: int,
        page_token: str | None,
    ) -> dict[str, Any]:
        params = {
            "query.term": query,
            "pageSize": page_size,
            "format": "json",
        }
        if page_token:
            params["pageToken"] = page_token

        url = f"{self.base_url}?{urlencode(params)}"
        with urlopen(url, timeout=self.timeout_seconds) as response:  # nosec B310
            body = response.read().decode("utf-8")
        return json.loads(body)

    def _to_trial(self, study: dict[str, Any]) -> RetrievedTrial:
        protocol = study.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        conditions_module = protocol.get("conditionsModule", {})
        eligibility_module = protocol.get("eligibilityModule", {})

        nct_id = identification.get("nctId", "unknown_nct")
        title = identification.get("briefTitle", "Untitled trial")
        conditions = conditions_module.get("conditions", []) or []
        criteria_text = eligibility_module.get("eligibilityCriteria", "") or ""
        parsed_criteria = parse_eligibility_criteria(criteria_text)

        return RetrievedTrial(
            nct_id=nct_id,
            title=title,
            conditions=conditions,
            criteria_text=criteria_text,
            parsed_criteria=parsed_criteria,
        )
