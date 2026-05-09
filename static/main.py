# =========================================================
# main.py
# KAMIZEN GOV AI
# FASTAPI SERVER
# =========================================================

import os
import json
import shutil
import uuid

from pathlib import Path
from datetime import datetime

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Request
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    FileResponse
)

from fastapi.staticfiles import StaticFiles

# =========================================================
# OCR
# =========================================================

try:
    import pytesseract
    from PIL import Image
except:
    pytesseract = None

# =========================================================
# ENGINE
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
# APP
# =========================================================

app = FastAPI(
    title="KAMIZEN GOV AI"
)

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

STATIC_DIR = BASE_DIR / "static"

UPLOADS_DIR = BASE_DIR / "uploads"

UPLOADS_DIR.mkdir(
    exist_ok=True
)

# =========================================================
# STATIC
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# =========================================================
# MEMORY CACHE
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

        return HTMLResponse(
            "<h1>index.html not found</h1>",
            status_code=404
        )

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
# SEARCH CONTRACTS
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

        return JSONResponse(
            status_code=500,
            content=error(str(e))
        )

# =========================================================
# CONTRACT ANALYSIS
# =========================================================

@app.post("/api/contracts/analyze")
async def analyze_contract_api(request: Request):

    try:

        body = await request.json()

        contract = body.get("contract", {})

        result = analyze_contract(contract)

        return {
            "success": True,
            "result": result
        }

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content=error(str(e))
        )

# =========================================================
# GENERATE PROPOSAL
# =========================================================

@app.post("/api/proposal/generate")
async def generate_proposal(request: Request):

    try:

        body = await request.json()

        contract = body.get("contract", {})

        summary = generate_ai_summary(contract)

        capability = generate_capability_statement(
            contract
        )

        outline = generate_proposal_outline(
            contract
        )

        proposal = {

            "proposal_id": str(uuid.uuid4()),

            "generated_at":
                str(datetime.utcnow()),

            "contract_title":
                contract.get("title", ""),

            "agency":
                contract.get("agency", ""),

            "executive_summary":
                summary,

            "capability_statement":
                capability,

            "proposal_outline":
                outline,

            "compliance_matrix":
                generate_compliance_matrix(
                    contract.get(
                        "description",
                        ""
                    )
                )
        }

        MEMORY["proposal_history"].append(
            proposal
        )

        return {
            "success": True,
            "proposal": proposal
        }

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content=error(str(e))
        )

# =========================================================
# OCR
# =========================================================

@app.post("/api/ocr")
async def run_ocr(
    file: UploadFile = File(...)
):

    try:

        ext = file.filename.split(".")[-1]

        filename = (
            f"{uuid.uuid4()}.{ext}"
        )

        file_path = UPLOADS_DIR / filename

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        extracted_text = ""

        # =================================================
        # OCR
        # =================================================

        if pytesseract:

            try:

                image = Image.open(file_path)

                extracted_text = (
                    pytesseract.image_to_string(
                        image
                    )
                )

            except Exception as img_error:

                extracted_text = (
                    f"OCR ERROR: {img_error}"
                )

        else:

            extracted_text = (
                "pytesseract not installed"
            )

        analysis = analyze_ocr_text(
            extracted_text
        )

        MEMORY["ocr_history"].append({

            "file": filename,
            "text": extracted_text,
            "analysis": analysis

        })

        return {

            "success": True,

            "filename": filename,

            "text": extracted_text,

            "analysis": analysis

        }

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content=error(str(e))
        )

# =========================================================
# CONTEXT ANALYSIS
# =========================================================

@app.post("/api/context")
async def context_api(request: Request):

    try:

        body = await request.json()

        text = body.get("text", "")

        context = get_context_topic(text)

        return {

            "success": True,

            "context": context

        }

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content=error(str(e))
        )

# =========================================================
# MEMORY
# =========================================================

@app.get("/api/memory")
async def get_memory():

    return {
        "success": True,
        "memory": MEMORY
    }

# =========================================================
# CLEAR MEMORY
# =========================================================

@app.post("/api/memory/clear")
async def clear_memory():

    MEMORY["contracts"] = []
    MEMORY["ocr_history"] = []
    MEMORY["proposal_history"] = []

    return {
        "success": True,
        "message": "Memory cleared"
    }

# =========================================================
# EXPORT PROPOSAL
# =========================================================

@app.post("/api/proposal/export")
async def export_proposal(request: Request):

    try:

        body = await request.json()

        proposal = body.get("proposal", {})

        export_id = str(uuid.uuid4())

        export_path = (
            UPLOADS_DIR /
            f"{export_id}.json"
        )

        with open(
            export_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                proposal,
                f,
                indent=2
            )

        return {

            "success": True,

            "export_id": export_id,

            "download":
                f"/api/download/{export_id}"

        }

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content=error(str(e))
        )

# =========================================================
# DOWNLOAD
# =========================================================

@app.get("/api/download/{file_id}")
async def download_file(file_id: str):

    try:

        file_path = (
            UPLOADS_DIR /
            f"{file_id}.json"
        )

        if not file_path.exists():

            raise HTTPException(
                status_code=404,
                detail="File not found"
            )

        return FileResponse(
            file_path,
            filename=f"{file_id}.json"
        )

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content=error(str(e))
        )

# =========================================================
# AI ASSIST
# =========================================================

@app.post("/api/assist")
async def ai_assist(request: Request):

    try:

        body = await request.json()

        prompt = body.get("prompt", "")

        response = {

            "analysis":
                "This opportunity appears relevant.",

            "recommendation":
                "Proceed with proposal generation.",

            "risk_level":
                "LOW",

            "next_steps": [

                "Generate capability statement",

                "Review compliance matrix",

                "Prepare pricing draft",

                "Submit before deadline"

            ]
        }

        return {

            "success": True,

            "prompt": prompt,

            "response": response

        }

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content=error(str(e))
        )

# =========================================================
# SERVER START
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                8000
            )
        ),
        reload=True
    )
