import json
import httpx
from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException
from ..config import ARS_MIN_SCORE, SLACK_WEBHOOK_URL, ARS_API_KEY
from ..services.flow_checks import scan_flow
from ..services.store import store_snapshot
from ..services.parsers.n8n import parse_n8n
from ..services.parsers.make import parse_make
from ..services.parsers.zapier import parse_zapier

router = APIRouter()

async def _post_slack_alert(webhook: str, text: str):
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            await client.post(webhook, json={"text": text})
    except Exception:
        pass

def _auth(x_ars_key: str | None):
    if not ARS_API_KEY:
        return
    if not x_ars_key or x_ars_key != ARS_API_KEY:
        raise HTTPException(status_code=401, detail="Missing/invalid X-ARS-Key")

@router.post("/scan/n8n")
async def scan_n8n(org: str = Form(...), name: str = Form("n8n-workflow"), file: UploadFile = File(...),
                   x_ars_key: str | None = Header(default=None, alias="X-ARS-Key")):
    _auth(x_ars_key)
    raw = json.loads((await file.read()).decode("utf-8", errors="ignore") or "{}")
    steps = parse_n8n(raw)
    findings = scan_flow("n8n", steps, raw)
    snap_id, score = await store_snapshot(org, {"org": org, "source": "n8n", "name": name}, findings)
    if SLACK_WEBHOOK_URL and score < ARS_MIN_SCORE:
        await _post_slack_alert(SLACK_WEBHOOK_URL, f":rotating_light: ARS score {score} below {ARS_MIN_SCORE} for {org} (source=n8n, name={name})")
    return {"snapshot_id": snap_id, "overall_score": score, "findings": findings}

@router.post("/scan/make")
async def scan_make(org: str = Form(...), name: str = Form("make-blueprint"), file: UploadFile = File(...),
                    x_ars_key: str | None = Header(default=None, alias="X-ARS-Key")):
    _auth(x_ars_key)
    raw = json.loads((await file.read()).decode("utf-8", errors="ignore") or "{}")
    steps = parse_make(raw)
    findings = scan_flow("make", steps, raw)
    snap_id, score = await store_snapshot(org, {"org": org, "source": "make", "name": name}, findings)
    if SLACK_WEBHOOK_URL and score < ARS_MIN_SCORE:
        await _post_slack_alert(SLACK_WEBHOOK_URL, f":rotating_light: ARS score {score} below {ARS_MIN_SCORE} for {org} (source=make, name={name})")
    return {"snapshot_id": snap_id, "overall_score": score, "findings": findings}

@router.post("/scan/zapier")
async def scan_zapier(org: str = Form(...), name: str = Form("zapier-export"), file: UploadFile = File(...),
                      x_ars_key: str | None = Header(default=None, alias="X-ARS-Key")):
    _auth(x_ars_key)
    raw = json.loads((await file.read()).decode("utf-8", errors="ignore") or "{}")
    steps = parse_zapier(raw)
    findings = scan_flow("zapier", steps, raw)
    snap_id, score = await store_snapshot(org, {"org": org, "source": "zapier", "name": name}, findings)
    if SLACK_WEBHOOK_URL and score < ARS_MIN_SCORE:
        await _post_slack_alert(SLACK_WEBHOOK_URL, f":rotating_light: ARS score {score} below {ARS_MIN_SCORE} for {org} (source=zapier, name={name})")
    return {"snapshot_id": snap_id, "overall_score": score, "findings": findings}
