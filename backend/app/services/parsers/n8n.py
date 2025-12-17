from __future__ import annotations
from typing import Any
from .common import NormalizedStep, safe_get

CODE_NODE_TYPES = {"n8n-nodes-base.code","n8n-nodes-base.function","n8n-nodes-base.functionItem","n8n-nodes-base.executeCommand"}
NETWORK_NODE_TYPES = {"n8n-nodes-base.httpRequest","n8n-nodes-base.webhook","n8n-nodes-base.emailSend","n8n-nodes-base.slack","n8n-nodes-base.telegram","n8n-nodes-base.discord","n8n-nodes-base.ssh"}

def parse_n8n(workflow: dict[str, Any]) -> list[NormalizedStep]:
    nodes = workflow.get("nodes") or []
    steps: list[NormalizedStep] = []
    for n in nodes:
        ntype = n.get("type") or ""
        name = n.get("name") or ntype
        params = n.get("parameters") or {}
        creds = bool(n.get("credentials"))
        is_public = (ntype == "n8n-nodes-base.webhook") or bool(safe_get(n, "webhookId"))
        can_exec = ntype in CODE_NODE_TYPES
        can_net = ntype in NETWORK_NODE_TYPES
        can_send = ntype in {"n8n-nodes-base.httpRequest","n8n-nodes-base.emailSend","n8n-nodes-base.slack","n8n-nodes-base.telegram","n8n-nodes-base.discord"}
        retry_like = bool(params.get("retryOnFail")) or bool(params.get("maxTries"))
        steps.append(NormalizedStep(name=name, kind=ntype, params=params, has_credentials=creds,
                                    is_public_entry=is_public, can_execute_code=can_exec,
                                    can_make_network_calls=can_net, can_send_data_out=can_send,
                                    retry_like=retry_like))
    return steps
