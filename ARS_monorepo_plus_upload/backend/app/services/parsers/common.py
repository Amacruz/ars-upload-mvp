from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class NormalizedStep:
    name: str
    kind: str
    params: dict
    has_credentials: bool = False
    is_public_entry: bool = False
    can_execute_code: bool = False
    can_make_network_calls: bool = False
    can_send_data_out: bool = False
    retry_like: bool = False

def safe_get(d: Any, *keys, default=None):
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur
