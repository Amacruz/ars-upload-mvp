from __future__ import annotations
from typing import Any
import re
from .parsers.common import NormalizedStep

def _finding(rule_id: str, severity: str, reason: str, asset_ref: str, rec_steps: list[str]):
    return {
        "rule_id": rule_id,
        "severity": severity,
        "asset_ref": asset_ref,
        "evidence": {"reason": reason},
        "recommendation": {"kind": "guidance", "steps": rec_steps},
        "status": "open",
    }

def scan_flow(source: str, steps: list[NormalizedStep], raw: dict[str, Any] | None = None) -> list[dict]:
    findings: list[dict] = []
    raw = raw or {}

    public_steps = [s for s in steps if s.is_public_entry]
    if public_steps:
        findings.append(_finding("ASI01","high","Public trigger/webhook detected. Add auth + validation.","flow",
                                 ["Require auth (token/HMAC). Validate schema. Add allow/deny rules for commands."]))

    net_steps = [s for s in steps if s.can_make_network_calls]
    if net_steps:
        findings.append(_finding("ASI02","high","Network/tool-capable steps detected. Add destination allowlists.","flow",
                                 ["Allowlist domains/hosts. Block arbitrary URLs. Validate tool outputs before acting."]))

    cred_steps = [s for s in steps if s.has_credentials]
    if cred_steps:
        findings.append(_finding("ASI03","high","Credentials/connections detected. Enforce least privilege.","flow",
                                 ["Use least-privilege scopes. Rotate keys. Avoid shared accounts."]))

    suspect = [s for s in steps if re.search(r"community|custom|third[-_ ]party", s.kind.lower())]
    if suspect:
        findings.append(_finding("ASI04","medium","Potential custom/community modules detected (supply-chain risk).","flow",
                                 ["Pin versions. Review vendor. Restrict permissions. Isolate network access."]))

    code_steps = [s for s in steps if s.can_execute_code]
    if code_steps:
        findings.append(_finding("ASI05","high","Code execution node detected (major risk area).","flow",
                                 ["Limit code nodes for untrusted inputs. Sandbox execution. Restrict file/network access."]))

    if public_steps and any(re.search(r"append|insert|write|upsert|create", str(s.params).lower()) for s in steps):
        findings.append(_finding("ASI06","high","Public trigger appears to write/store data (poisoning/persistence risk).","flow",
                                 ["Validate/clean inputs. Tag trust levels. Quarantine suspicious entries. Add TTL/retention."]))

    if any(re.search(r"agent|assistant|llm|openai|anthropic|bedrock", s.kind.lower()) for s in steps) and net_steps:
        findings.append(_finding("ASI07","medium","AI/agent step plus network steps. Secure message integrity.","flow",
                                 ["Sign requests. Use mTLS where possible. Validate all tool outputs."]))

    if any(s.retry_like for s in steps):
        findings.append(_finding("ASI08","medium","Retry/loop behavior detected (runaway executions).","flow",
                                 ["Set max retries. Add circuit breakers. Enforce budgets (time/cost/request)."]))

    if any(s.can_send_data_out for s in steps):
        findings.append(_finding("ASI09","medium","Outbound messaging/data send detected.","flow",
                                 ["Add approval for high-impact sends. Redact secrets/PII. Add logging."]))

    findings.append(_finding("ASI10","medium","Ensure only approved workflows run (registry/allowlist).","flow",
                             ["Maintain an allowlist of approved workflows. Require review for changes. Disable unknown clones."]))

    text = str(raw)
    if re.search(r"https?://\$\{\{|https?://\$\(", text, re.IGNORECASE):
        findings.append(_finding("FLOW-HTTP-001","high","Dynamic URL construction detected (SSRF/exfil risk).","flow",
                                 ["Allowlist domains. Validate URL params. Block internal IP ranges."]))

    if re.search(r"sk-[A-Za-z0-9]{20,}|api[_-]?key\s*[:=]\s*[A-Za-z0-9\-_]{12,}", text):
        findings.append(_finding("ARS-SECR-001","critical","Potential secret-like token detected in export.","flow",
                                 ["Move secrets to credential store/vault. Rotate any exposed keys immediately."]))
    return findings
