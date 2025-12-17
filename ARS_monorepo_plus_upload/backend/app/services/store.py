from sqlalchemy import select
from ..db import SessionLocal
from ..models import Org, Snapshot, Finding
from ..services.scoring import compute_overall

async def store_snapshot(org_name: str, meta: dict | None, findings: list[dict]) -> tuple[int, int]:
    score = compute_overall(findings)
    async with SessionLocal() as session:
        res = await session.execute(select(Org).where(Org.name == org_name))
        org = res.scalar_one_or_none()
        if not org:
            org = Org(name=org_name)
            session.add(org)
            await session.flush()
        snap = Snapshot(org_id=org.id, overall_score=score, meta=meta or {"org": org_name})
        session.add(snap)
        await session.flush()
        for f in findings:
            session.add(Finding(
                snapshot_id=snap.id,
                rule_id=f.get("rule_id", "UNKNOWN"),
                severity=f.get("severity", "low"),
                asset_ref=f.get("asset_ref"),
                evidence=f.get("evidence"),
                recommendation=f.get("recommendation"),
                status=f.get("status") or "open",
            ))
        await session.commit()
    return snap.id, score
