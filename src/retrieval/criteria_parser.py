from dataclasses import dataclass, field


@dataclass
class ParsedEligibilityCriteria:
    inclusion_criteria: list[str] = field(default_factory=list)
    exclusion_criteria: list[str] = field(default_factory=list)
    uncategorized: list[str] = field(default_factory=list)


def _normalize_line(line: str) -> str:
    cleaned = line.strip().lstrip("-*0123456789. ").strip()
    return cleaned


def parse_eligibility_criteria(criteria_text: str | None) -> ParsedEligibilityCriteria:
    if not criteria_text:
        return ParsedEligibilityCriteria()

    result = ParsedEligibilityCriteria()
    section = "uncategorized"

    for raw_line in criteria_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        lowered = line.lower()
        if "inclusion criteria" in lowered:
            section = "inclusion"
            continue
        if "exclusion criteria" in lowered:
            section = "exclusion"
            continue

        normalized = _normalize_line(line)
        if not normalized:
            continue

        if section == "inclusion":
            result.inclusion_criteria.append(normalized)
        elif section == "exclusion":
            result.exclusion_criteria.append(normalized)
        else:
            result.uncategorized.append(normalized)

    return result
