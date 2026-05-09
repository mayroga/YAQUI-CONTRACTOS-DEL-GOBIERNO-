# =========================================================
# contracts_engine.py
# GOV CONTRACT AI ENGINE - KAMIZEN GOV SYSTEM v2
# =========================================================

import os
import re
import json
import uuid
from datetime import datetime

# =========================================================
# COMPANY PROFILE
# =========================================================

COMPANY_PROFILE = {
    "company_name": "KAMIZEN",
    "naics": [
        "541511",
        "541512",
        "541519",
        "611710",
        "611430"
    ],
    "capabilities": [
        "interactive training systems",
        "behavioral regulation",
        "adaptive learning",
        "emotional resilience",
        "human performance",
        "cognitive readiness",
        "stress regulation",
        "AI learning systems"
    ]
}

# =========================================================
# SCORE RULES
# =========================================================

SCORE_RULES = {
    "training": 15,
    "education": 10,
    "software": 10,
    "ai": 15,
    "behavioral": 20,
    "resilience": 20,
    "human": 20,
    "performance": 20,
    "cognitive": 20,
    "learning": 15,
    "stress": 15,
    "support": 10
}

# =========================================================
# HELPERS
# =========================================================

def clean_text(text):
    if not text:
        return ""

    text = str(text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================================================
# KEYWORDS
# =========================================================

def extract_keywords(text):
    text = clean_text(text).lower()
    return [k for k in SCORE_RULES.keys() if k in text]


# =========================================================
# SCORE ENGINE
# =========================================================

def calculate_contract_score(text):
    text = clean_text(text).lower()

    score = 0
    matched = []

    for k, v in SCORE_RULES.items():
        if k in text:
            score += v
            matched.append(k)

    return {
        "score": score,
        "matched_keywords": matched
    }


# =========================================================
# NAICS MATCH
# =========================================================

def match_naics(naics):
    if not naics:
        return False

    if isinstance(naics, list):
        return any(n in COMPANY_PROFILE["naics"] for n in naics)

    return naics in COMPANY_PROFILE["naics"]


# =========================================================
# CONTRACT ANALYSIS
# =========================================================

def analyze_contract(contract):

    contract = {
        "id": str(uuid.uuid4()),
        "title": clean_text(contract.get("title", "")),
        "agency": clean_text(contract.get("agency", "")),
        "description": clean_text(contract.get("description", "")),
        "naics": contract.get("naics", []),
        "url": contract.get("url", "")
    }

    combined = f"{contract['title']} {contract['description']}"

    score_data = calculate_contract_score(combined)
    naics_ok = match_naics(contract["naics"])

    score = score_data["score"]
    if naics_ok:
        score += 25

    level = "LOW"
    if score >= 80:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"

    return {
        "contract": contract,
        "score": score,
        "level": level,
        "keywords": score_data["matched_keywords"],
        "naics_match": naics_ok
    }


# =========================================================
# SAM SEARCH (DEMO)
# =========================================================

def search_sam_contracts(keyword="training"):

    demo = [
        {
            "title": "Student Behavioral Training System",
            "agency": "Department of Education",
            "description": "Adaptive learning platform for student emotional resilience and behavioral support.",
            "naics": ["541511", "611710"],
            "url": "https://sam.gov"
        },
        {
            "title": "Human Performance AI Platform",
            "agency": "Department of Defense",
            "description": "AI system for cognitive readiness and training optimization.",
            "naics": ["541512"],
            "url": "https://sam.gov"
        }
    ]

    results = []

    for c in demo:
        combined = (c["title"] + " " + c["description"]).lower()

        if keyword.lower() in combined:
            results.append(analyze_contract(c))

    return sorted(results, key=lambda x: x["score"], reverse=True)


# =========================================================
# RFP REQUIREMENTS
# =========================================================

def extract_rfp_requirements(text):

    text = clean_text(text).lower()

    keywords = ["must", "shall", "required", "mandatory", "deadline", "security"]

    found = [k for k in keywords if k in text]

    return {
        "requirements_found": found,
        "length": len(text)
    }


# =========================================================
# CAPABILITY STATEMENT
# =========================================================

def generate_capability_statement(contract):

    return clean_text(f"""
KAMIZEN provides AI-driven training systems focused on behavioral
support, cognitive readiness, and adaptive learning.

Agency: {contract.get("agency", "")}

Core capabilities include:
{", ".join(COMPANY_PROFILE["capabilities"])}
""")


# =========================================================
# PROPOSAL OUTLINE
# =========================================================

def generate_proposal_outline(contract):

    return {
        "title": f"Proposal - {contract.get('title','')}",
        "sections": [
            "Executive Summary",
            "Technical Approach",
            "Capabilities",
            "Implementation Plan",
            "Compliance",
            "Risk Mitigation",
            "Pricing"
        ]
    }


# =========================================================
# AI SUMMARY
# =========================================================

def generate_ai_summary(contract):

    return f"""
Opportunity: {contract.get('title','')}

Focus: {contract.get('description','')}

KAMIZEN is aligned due to AI training,
behavioral systems, and cognitive readiness capabilities.
"""


# =========================================================
# OCR ANALYSIS (FIXED - IMPORTANT)
# =========================================================

def analyze_ocr_text(text):

    # 🚨 FIX: handle empty OCR
    if not text or len(text.strip()) < 3:
        return {
            "error": "No readable text detected from image",
            "context": {},
            "keywords": [],
            "score": {"score": 0, "matched_keywords": []},
            "raw_text": ""
        }

    context = {}

    lower = text.lower()

    if "student" in lower:
        context["sector"] = "education"

    if "training" in lower:
        context["sector"] = "training"

    if "software" in lower:
        context["sector"] = "software"

    keywords = extract_keywords(text)
    score = calculate_contract_score(text)

    return {
        "context": context,
        "keywords": keywords,
        "score": score,
        "raw_text": text
    }


# =========================================================
# ENGINE MAIN
# =========================================================

def run_contract_engine(query="training"):

    contracts = search_sam_contracts(query)

    output = []

    for c in contracts:

        contract = c["contract"]

        output.append({
            "contract": contract,
            "score": c["score"],
            "level": c["level"],
            "keywords": c["keywords"],
            "summary": generate_ai_summary(contract),
            "capability_statement": generate_capability_statement(contract),
            "proposal_outline": generate_proposal_outline(contract)
        })

    return output


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(json.dumps(run_contract_engine("training"), indent=2))
