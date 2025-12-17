from __future__ import annotations
from typing import Any
from .common import NormalizedStep

CODE_HINTS = {"javascript","code","script"}
NETWORK_HINTS = {"http","webhook","email","slack","telegram","discord","ftp","ssh"}

def parse_make(blueprint: dict[str, Any]) -> list[NormalizedStep]:
    modules = blueprint.get("modules") or blueprint.get("flow") or []
    if isinstance(modules, dict):
        modules = modules.get("modules") or []
    steps: list[NormalizedStep] = []
    for m in modules:
        kind = (m.get("module") or m.get("type") or m.get("name") or "make-module")
        name = m.get("name") or kind
        params = m.get("parameters") or m.get("settings") or {}
        k = str(kind).lower()
        can_exec = any(h in k for h in CODE_HINTS)
        can_net = any(h in k for h in NETWORK_HINTS)
        is_public = "webhook" in k and ("custom" in k or "trigger" in k)
        has_creds = bool(m.get("connection")) or bool(m.get("connections")) or bool(m.get("credentials"))
        steps.append(NormalizedStep(name=name, kind=str(kind), params=params if isinstance(params, dict) else {"raw": params},
                                    has_credentials=has_creds, is_public_entry=is_public,
                                    can_execute_code=can_exec, can_make_network_calls=can_net,
                                    can_send_data_out=can_net, retry_like=bool(params.get("retries")) if isinstance(params, dict) else False))
    return steps
