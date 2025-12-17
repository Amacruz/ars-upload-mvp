from __future__ import annotations
from typing import Any
from .common import NormalizedStep

CODE_HINTS = {"code","javascript","python"}
NETWORK_HINTS = {"webhook","http","request","email","slack","discord","telegram"}

def parse_zapier(zap: dict[str, Any]) -> list[NormalizedStep]:
    steps_raw = zap.get("steps") or zap.get("actions") or zap.get("workflow") or []
    if isinstance(steps_raw, dict):
        steps_raw = steps_raw.get("steps") or steps_raw.get("actions") or []
    steps: list[NormalizedStep] = []
    for s in steps_raw:
        kind = s.get("type") or s.get("app") or s.get("key") or "zap-step"
        name = s.get("name") or kind
        params = s.get("params") or s.get("settings") or s.get("config") or {}
        k = str(kind).lower()
        can_exec = any(h in k for h in CODE_HINTS)
        can_net = any(h in k for h in NETWORK_HINTS)
        is_public = "webhook" in k and ("catch" in k or "trigger" in k)
        has_creds = bool(s.get("account")) or bool(s.get("auth")) or bool(s.get("connection"))
        steps.append(NormalizedStep(name=name, kind=str(kind), params=params if isinstance(params, dict) else {"raw": params},
                                    has_credentials=has_creds, is_public_entry=is_public,
                                    can_execute_code=can_exec, can_make_network_calls=can_net,
                                    can_send_data_out=can_net, retry_like=bool(params.get("retries")) if isinstance(params, dict) else False))
    return steps
