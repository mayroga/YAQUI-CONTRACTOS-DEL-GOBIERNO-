# =========================================================
# contracts_engine.py
# GOV CONTRACT AI ENGINE
# KAMIZEN GOV SYSTEM
# =========================================================

import os
import re
import json
import uuid
import requests
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# =========================================================
# COMPANY PROFILE
# =========================================================

COMPANY_PROFILE = {
    "company_name": "KAMIZEN",
    "uei": "",
    "cage_code": "",
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
        "guided training",
        "multimodal AI systems",
        "interactive wellness technology"
    ],
    "keywords": [
        "training",
        "resilience",
        "behavioral",
        "student support",
        "interactive software",
        "human performance",
        "adaptive learning",
        "AI",
        "focus",
        "wellness",
        "education",
        "cognitive"
    ],
    "agencies": [
        "Department of Education",
        "Department of Defense",
        "VA",
        "Homeland Security"
    ]
}

# =========================================================
# SCORE WEIGHTS
# =========================================================

SCORE_RULES = {
    "resilience": 15,
    "behavioral": 20,
    "student": 15,
    "training": 15,
    "interactive": 15,
    "software": 10,
    "wellness": 10,
    "adaptive": 20,
    "AI": 15,
    "education": 10,
    "human performance": 25,
    "cognitive": 20,
    "stress": 20,
    "learning": 15,
    "support": 10
}

# =========================================================
# BASIC HELPERS
# =========================================================

def clean_text(text):
    if not text:
        return ""

    text = str(text)
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()

# =========================================================
# EXTRACT KEYWORDS
# =========================================================

def extract_keywords(text):

    text = clean_text(text).lower()

    found = []

    for word in SCORE_RULES.keys():

        if word.lower() in text:
            found.append(word)

    return found

# =========================================================
# CONTRACT SCORE
# =========================================================

def calculate_contract_score(text):

    text = clean_text(text).lower()

    score = 0

    matched = []

    for keyword, value in SCORE_RULES.items():

        if keyword.lower() in text:
            score += value
            matched.append(keyword)

    return {
        "score": score,
        "matched_keywords": matched
    }

# =========================================================
# NAICS MATCHING
# =========================================================

def match_naics(contract_naics):

    if not contract_naics:
        return False

    if isinstance(contract_naics, list):

        for code in contract_naics:

            if code in COMPANY_PROFILE["naics"]:
                return True

    else:

        if contract_naics in COMPANY_PROFILE["naics"]:
            return True

    return False

# =========================================================
# OPPORTUNITY CLASSIFIER
# =========================================================

def classify_opportunity(contract):

    title = clean_text(contract.get("title", ""))
    description = clean_text(contract.get("description", ""))

    combined = f"{title} {description}"

    result = calculate_contract_score(combined)

    score = result["score"]

    level = "LOW"

    if score >= 80:
        level = "HIGH"

    elif score >= 40:
        level = "MEDIUM"

    return {
        "score": score,
        "level": level,
        "keywords": result["matched_keywords"]
    }

# =========================================================
# CONTRACT NORMALIZER
# =========================================================

def normalize_contract(data):

    return {
        "id": str(uuid.uuid4()),
        "title": clean_text(data.get("title", "")),
        "agency": clean_text(data.get("agency", "")),
        "description": clean_text(data.get("description", "")),
        "naics": data.get("naics", []),
        "posted_date": data.get("posted_date", ""),
        "due_date": data.get("due_date", ""),
        "url": data.get("url", ""),
        "source": data.get("source", "unknown")
    }

# =========================================================
# CONTRACT MATCH ENGINE
# =========================================================

def analyze_contract(contract):

    contract = normalize_contract(contract)

    title = contract["title"]
    description = contract["description"]

    combined = f"{title} {description}"

    classification = classify_opportunity(contract)

    naics_match = match_naics(contract["naics"])

    final_score = classification["score"]

    if naics_match:
        final_score += 25

    return {
        "contract": contract,
        "match": naics_match,
        "score": final_score,
        "level": classification["level"],
        "keywords": classification["keywords"]
    }

# =========================================================
# SIMPLE SAM SEARCH
# =========================================================

def search_sam_contracts(keyword="training"):

    # =====================================================
    # NOTE:
    # This is placeholder structure.
    # You can replace with official SAM API later.
    # =====================================================

    demo_contracts = [

        {
            "title": "Student Behavioral Training Platform",
            "agency": "Department of Education",
            "description": "Seeking adaptive behavioral training software for student emotional support and resilience.",
            "naics": ["541511", "611710"],
            "posted_date": "2026-05-01",
            "due_date": "2026-06-01",
            "source": "SAM.gov",
            "url": "https://sam.gov"
        },

        {
            "title": "Human Performance Readiness System",
            "agency": "Department of Defense",
            "description": "Interactive resilience and cognitive readiness software platform.",
            "naics": ["541512"],
            "posted_date": "2026-05-04",
            "due_date": "2026-06-15",
            "source": "SAM.gov",
            "url": "https://sam.gov"
        }

    ]

    results = []

    for item in demo_contracts:

        combined = (
            item["title"] +
            " " +
            item["description"]
        ).lower()

        if keyword.lower() in combined:

            analyzed = analyze_contract(item)

            results.append(analyzed)

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    return results

# =========================================================
# RFP REQUIREMENTS EXTRACTION
# =========================================================

def extract_rfp_requirements(text):

    text = clean_text(text)

    lower = text.lower()

    requirements = []

    patterns = [
        "must",
        "required",
        "mandatory",
        "shall",
        "minimum",
        "deadline",
        "security clearance"
    ]

    for pattern in patterns:

        if pattern in lower:
            requirements.append(pattern)

    return {
        "requirements_found": requirements,
        "text_length": len(text)
    }

# =========================================================
# CAPABILITY STATEMENT
# =========================================================

def generate_capability_statement(contract):

    company = COMPANY_PROFILE["company_name"]

    agency = contract.get("agency", "")

    capabilities = ", ".join(
        COMPANY_PROFILE["capabilities"]
    )

    statement = f"""
{company} delivers advanced interactive training
and adaptive human performance systems focused on
behavioral readiness, emotional resilience,
cognitive support, and multimodal engagement.

Our capabilities include:

{capabilities}

We support federal agencies including
the {agency} with scalable digital systems
designed for training, resilience,
engagement, and adaptive learning.

NAICS:
{", ".join(COMPANY_PROFILE["naics"])}
"""

    return clean_text(statement)

# =========================================================
# COMPLIANCE MATRIX
# =========================================================

def generate_compliance_matrix(rfp_text):

    requirements = extract_rfp_requirements(rfp_text)

    matrix = []

    for req in requirements["requirements_found"]:

        matrix.append({
            "requirement": req,
            "status": "PENDING REVIEW"
        })

    return matrix

# =========================================================
# PROPOSAL OUTLINE
# =========================================================

def generate_proposal_outline(contract):

    title = contract.get("title", "")

    return {
        "proposal_title": f"Proposal Response - {title}",
        "sections": [

            "Executive Summary",
            "Technical Approach",
            "Capabilities",
            "Implementation Plan",
            "Personnel",
            "Past Performance",
            "Compliance Matrix",
            "Pricing",
            "Risk Mitigation",
            "Conclusion"

        ]
    }

# =========================================================
# AI CONTRACT SUMMARY
# =========================================================

def generate_ai_summary(contract):

    title = contract.get("title", "")
    description = contract.get("description", "")

    return f"""
This opportunity appears related to
{title}.

The contract focuses on:

{description}

KAMIZEN appears compatible due to its
capabilities in adaptive training,
interactive systems, emotional resilience,
human performance, and behavioral support.
"""

# =========================================================
# CONTEXT DETECTOR
# =========================================================

def get_context_topic(screen_text):

    screen_text = clean_text(screen_text)

    lower = screen_text.lower()

    tags = []

    agencies = []

    probable_naics = []

    if "student" in lower:
        tags.append("education")
        probable_naics.append("611710")

    if "training" in lower:
        tags.append("training")
        probable_naics.append("611430")

    if "software" in lower:
        tags.append("software")
        probable_naics.append("541511")

    if "defense" in lower:
        agencies.append("Department of Defense")

    if "veteran" in lower:
        agencies.append("VA")

    if "school" in lower:
        agencies.append("Department of Education")

    return {
        "tags": list(set(tags)),
        "agencies": list(set(agencies)),
        "probable_naics": list(set(probable_naics))
    }

# =========================================================
# OCR PLACEHOLDER
# =========================================================

def analyze_ocr_text(text):

    context = get_context_topic(text)

    keywords = extract_keywords(text)

    score_data = calculate_contract_score(text)

    return {
        "context": context,
        "keywords": keywords,
        "score": score_data
    }

# =========================================================
# MASTER ENGINE
# =========================================================

def run_contract_engine(query="training"):

    contracts = search_sam_contracts(query)

    results = []

    for item in contracts:

        contract = item["contract"]

        summary = generate_ai_summary(contract)

        capability = generate_capability_statement(contract)

        proposal = generate_proposal_outline(contract)

        results.append({

            "contract": contract,
            "score": item["score"],
            "level": item["level"],
            "keywords": item["keywords"],
            "summary": summary,
            "capability_statement": capability,
            "proposal_outline": proposal

        })

    return results

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    data = run_contract_engine("training")

    print(
        json.dumps(
            data,
            indent=2
        )
    )
