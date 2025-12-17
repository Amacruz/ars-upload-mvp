from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER

def build_pdf(path: str, score: int, findings: list[dict], meta: dict | None = None):
    c = canvas.Canvas(path, pagesize=LETTER)
    _, h = LETTER
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, h - 60, "Agent Risk Snapshot — Executive Report")
    c.setFont("Helvetica", 11)
    if meta:
        c.drawString(40, h - 80, f"Org: {meta.get('org','-')}   Source: {meta.get('source','-')}   Name: {meta.get('name','-')}")
    c.drawString(40, h - 98, f"Overall Score: {score}")
    y = h - 130
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Top Findings")
    y -= 16
    c.setFont("Helvetica", 10)
    for f in findings[:28]:
        line = f"- {f.get('rule_id','?')} [{f.get('severity','?')}] {(f.get('evidence') or {}).get('reason','')}"
        c.drawString(40, y, line[:110])
        y -= 12
        if y < 70:
            c.showPage()
            y = h - 70
            c.setFont("Helvetica", 10)
    c.showPage()
    c.save()
