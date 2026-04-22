from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TrialCriteria:
    trial_id: str
    title: str
    min_age: int | None = None
    max_age: int | None = None
    required_conditions: List[str] = field(default_factory=list)
    excluded_conditions: List[str] = field(default_factory=list)
    excluded_medications: List[str] = field(default_factory=list)
    required_labs_min: Dict[str, float] = field(default_factory=dict)
    required_labs_max: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.trial_id.strip():
            raise ValueError("trial_id must be non-empty")
        if not self.title.strip():
            raise ValueError("title must be non-empty")
        if self.min_age is not None and self.max_age is not None and self.min_age > self.max_age:
            raise ValueError("min_age cannot be greater than max_age")

        self.required_conditions = [c.lower() for c in self.required_conditions]
        self.excluded_conditions = [c.lower() for c in self.excluded_conditions]
        self.excluded_medications = [m.lower() for m in self.excluded_medications]
        self.required_labs_min = {k.lower(): float(v) for k, v in self.required_labs_min.items()}
        self.required_labs_max = {k.lower(): float(v) for k, v in self.required_labs_max.items()}
