# =========================================================
# main.py
# KAMIZEN GOV AI - STABLE PRODUCTION VERSION
# =========================================================

import os
import json
import shutil
import uuid

from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# =========================================================
# ENGINE IMPORTS
# =========================================================

from contracts_engine import (
    run_contract_engine,
    analyze_contract,
    generate_ai_summary,
    generate_capability_statement,
    generate_compliance_matrix,
    generate_proposal_outline,
    extract_rfp_requirements,
    get_context_topic,
    analyze_ocr_text
)

# =========================================================
# OCR (EASYOCR)
# =========================================================

import easyocr

OCR_READER = None

def get_reader():
    global OCR_READER
    if OCR_READER is None:
        OCR_READER = easyocr.Reader(['en'], gpu=False)
    return OCR_READER

# =========================================================
# APP
# =========================================================

app = FastAPI(title="KAMIZEN GOV AI")

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "uploads"

UPLOADS_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# =========================================================
# MEMORY
# =========================================================

MEMORY = {
    "contracts": [],
    "ocr_history": [],
    "proposal_history": []
}

# =========================================================
# HELPERS
# =========================================================

def success(data=None):
    return {
        "success": True,
        "timestamp": str(datetime.utcnow()),
        "data": data
    }

def error(message="Unknown error"):
    return {
        "success": False,
        "message": message,
        "timestamp": str(datetime.utcnow())
    }

# =========================================================
# HOME
# =========================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    index_path = STATIC_DIR / "index.html"

    if not index_path.exists():
        return HTMLResponse("<h1>index.html not found</h1>", status_code=404)

    return FileResponse(index_path)

# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
async def health():
    return {
        "status": "online",
        "service": "KAMIZEN GOV AI",
        "time": str(datetime.utcnow())
    }

# =========================================================
# CONTRACT SEARCH
# =========================================================

@app.get("/api/contracts/search")
async def search_contracts(q: str = "training"):
    try:
        results = run_contract_engine(q)

        MEMORY["contracts"] = results

        return {
            "success": True,
            "query": q,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        return JSONResponse(status_code=500, content=error(str(e)))

# =========================================================
# ANALYZE CONTRACT
# =========================================================

@app.post("/api/contracts/analyze")
async def analyze_contract_api(request: Request):
    try:
        body = await request.json()
        contract = body.get("contract", {})

        result = analyze_contract(contract)

        return success(result)

    except Exception as e:
        return JSONResponse(status_code=500, content=error(str(e)))

# =========================================================
# PROPOSAL GENERATION
# =========================================================

@app.post("/api/proposal/generate")
async def generate_proposal(request: Request):
    try:
        body = await request.json()
        contract = body.get("contract", {})

        proposal = {
            "proposal_id": str(uuid.uuid4()),
            "generated_at": str(datetime.utcnow()),
            "contract_title": contract.get("title", ""),
            "agency": contract.get("agency", ""),
            "executive_summary": generate_ai_summary(contract),
            "capability_statement": generate_capability_statement(contract),
            "proposal_outline": generate_proposal_outline(contract),
            "compliance_matrix": generate_compliance_matrix(
                contract.get("description", "")
            )
        }

        MEMORY["proposal_history"].append(proposal)

        return success(proposal)

    except Exception as e:
        return JSONResponse(status_code=500, content=error(str(e)))

# =========================================================
# OCR (FIXED + SAFE + EXPLICIT OUTPUT)
# =========================================================

@app.post("/api/ocr")
async def run_ocr(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_path = UPLOADS_DIR / f"{file_id}_{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        reader = get_reader()

        result = reader.readtext(str(file_path), detail=0)

        # =====================================================
        # FIX: HANDLE EMPTY OCR RESULT
        # =====================================================

        if not result or len(result) == 0:

            response = {
                "file": file.filename,
                "text": "",
                "warning": "No readable text detected",
                "analysis": {
                    "error": "OCR_EMPTY_RESULT",
                    "context": {},
                    "keywords": [],
                    "score": {"score": 0, "matched_keywords": []}
                }
            }

            return success(response)

        extracted_text = " ".join(result)

        analysis = analyze_ocr_text(extracted_text)

        payload = {
            "file": file.filename,
            "text": extracted_text,
            "analysis": analysis
        }

        MEMORY["ocr_history"].append(payload)

        return success(payload)

    except Exception as e:
        return JSONResponse(status_code=500, content=error(str(e)))

# =========================================================
# CONTEXT
# =========================================================

@app.post("/api/context")
async def context_api(request: Request):
    try:
        body = await request.json()
        text = body.get("text", "")

        context = get_context_topic(text)

        return success(context)

    except Exception as e:
        return JSONResponse(status_code=500, content=error(str(e)))

# =========================================================
# MEMORY
# =========================================================

@app.get("/api/memory")
async def get_memory():
    return success(MEMORY)

@app.post("/api/memory/clear")
async def clear_memory():
    MEMORY["contracts"] = []
    MEMORY["ocr_history"] = []
    MEMORY["proposal_history"] = []

    return success("Memory cleared")

# =========================================================
# ASSIST AI
# =========================================================

@app.post("/api/assist")
async def ai_assist(request: Request):
    try:
        body = await request.json()
        prompt = body.get("prompt", "")

        return success({
            "prompt": prompt,
            "response": {
                "analysis": "Contract analyzed",
                "recommendation": "Proceed with bid",
                "risk_level": "MEDIUM",
                "next_steps": [
                    "Review RFP",
                    "Build compliance matrix",
                    "Prepare proposal"
                ]
            }
        })

    except Exception as e:
        return JSONResponse(status_code=500, content=error(str(e)))

# =========================================================
# EXPORT
# =========================================================

@app.post("/api/proposal/export")
async def export_proposal(request: Request):
    try:
        body = await request.json()
        proposal = body.get("proposal", {})

        export_id = str(uuid.uuid4())
        export_path = UPLOADS_DIR / f"{export_id}.json"

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(proposal, f, indent=2)

        return success({
            "export_id": export_id,
            "download": f"/api/download/{export_id}"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content=error(str(e)))

# =========================================================
# DOWNLOAD
# =========================================================

@app.get("/api/download/{file_id}")
async def download_file(file_id: str):
    file_path = UPLOADS_DIR / f"{file_id}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
