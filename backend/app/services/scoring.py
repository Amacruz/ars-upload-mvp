SEVERITY_PENALTY = {"low": 1, "medium": 2, "high": 4, "critical": 6}

def compute_overall(findings: list[dict] | None) -> int:
    findings = findings or []
    penalty = 0
    for f in findings:
        sev = (f.get("severity") or "low").lower()
        penalty += SEVERITY_PENALTY.get(sev, 2)
    return max(0, 100 - penalty * 3)
