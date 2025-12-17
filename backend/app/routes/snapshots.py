import os, tempfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..db import SessionLocal
from ..models import Snapshot, Finding
from ..pdf import build_pdf

router = APIRouter()

@router.get("/snapshots/{snap_id}")
async def get_snapshot(snap_id: int):
    async with SessionLocal() as session:
        q = select(Snapshot).where(Snapshot.id == snap_id).options(selectinload(Snapshot.org))
        s = (await session.execute(q)).scalar_one_or_none()
        if not s:
            raise HTTPException(404, "snapshot not found")
        fs = (await session.execute(select(Finding).where(Finding.snapshot_id == s.id))).scalars().all()
        findings = [{
            "rule_id": f.rule_id,
            "severity": f.severity,
            "asset_ref": f.asset_ref,
            "evidence": f.evidence,
            "recommendation": f.recommendation,
            "status": f.status,
        } for f in fs]
        return {"snapshot_id": s.id, "overall_score": s.overall_score, "meta": s.meta, "findings": findings}

@router.get("/snapshots/{snap_id}/export.pdf")
async def export_snapshot_pdf(snap_id: int):
    async with SessionLocal() as session:
        s = (await session.execute(select(Snapshot).where(Snapshot.id == snap_id))).scalar_one_or_none()
        if not s:
            raise HTTPException(404, "snapshot not found")
        fs = (await session.execute(select(Finding).where(Finding.snapshot_id == s.id))).scalars().all()
        findings = [{"rule_id": f.rule_id, "severity": f.severity, "asset_ref": f.asset_ref or "-", "evidence": f.evidence or {}} for f in fs]
    tmpdir = tempfile.mkdtemp()
    pdf_path = os.path.join(tmpdir, f"ARS_snapshot_{snap_id}.pdf")
    build_pdf(pdf_path, s.overall_score, findings, s.meta or {})
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"ARS_snapshot_{snap_id}.pdf")
