from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .db import init_db
from .routes.scan import router as scan_router
from .routes.snapshots import router as snapshots_router

app = FastAPI(title="Agent Risk Snapshot (Upload MVP)")
app.include_router(scan_router, prefix="/v1")
app.include_router(snapshots_router, prefix="/v1")
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/upload", response_class=HTMLResponse)
async def upload(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})
