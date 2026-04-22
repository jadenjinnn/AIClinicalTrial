from dataclasses import dataclass
import re

from src.retrieval.ctgov_client import RetrievedTrial


def _tokenize(text: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", text.lower()) if token}


@dataclass
class RankedTrial:
    trial: RetrievedTrial
    score: float


class InMemoryTrialIndexer:
    def __init__(self) -> None:
        self._trials: list[RetrievedTrial] = []

    def add_trials(self, trials: list[RetrievedTrial]) -> None:
        self._trials.extend(trials)

    def search(self, query: str, top_k: int = 5) -> list[RankedTrial]:
        query_tokens = _tokenize(query)
        ranked: list[RankedTrial] = []
        for trial in self._trials:
            haystack = " ".join(
                [trial.title, " ".join(trial.conditions), trial.criteria_text]
            )
            trial_tokens = _tokenize(haystack)
            overlap = len(query_tokens.intersection(trial_tokens))
            score = overlap / max(1, len(query_tokens))
            ranked.append(RankedTrial(trial=trial, score=score))

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:top_k]
