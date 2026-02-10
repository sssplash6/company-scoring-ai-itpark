from __future__ import annotations

import json
from typing import Dict, List, Optional, Tuple

from openai import OpenAI

from .models import CriterionScore, Scorecard
from .utils import html_to_text


DEFAULT_MODEL = "gpt-4.1-mini"

DEFAULT_CRITERIA = [
    {"id": "identity_website_quality", "name": "Official website quality", "category": "Identity"},
    {"id": "identity_contact_info", "name": "Contact information presence", "category": "Identity"},
    {"id": "identity_legal_identifiers", "name": "Legal or company identifiers", "category": "Identity"},
    {"id": "identity_brand_consistency", "name": "Branding consistency", "category": "Identity"},
    {"id": "identity_address_presence", "name": "Physical address presence", "category": "Identity"},
    {"id": "identity_leadership_visibility", "name": "Leadership visibility", "category": "Identity"},

    {"id": "history_years_in_business", "name": "Years in business", "category": "History"},
    {"id": "history_founding_story", "name": "Founding story clarity", "category": "History"},
    {"id": "history_milestones", "name": "Milestones or timeline presence", "category": "History"},

    {"id": "scale_headcount", "name": "Headcount or scale signals", "category": "Scale"},
    {"id": "scale_growth", "name": "Growth indicators", "category": "Scale"},
    {"id": "scale_hiring", "name": "Hiring or capacity signals", "category": "Scale"},

    {"id": "capacity_delivery", "name": "Delivery capacity signals", "category": "Capacity"},
    {"id": "capacity_pm", "name": "Project management capacity", "category": "Capacity"},
    {"id": "capacity_qa", "name": "QA or testing capacity", "category": "Capacity"},

    {"id": "tech_stack_clarity", "name": "Tech stack clarity", "category": "Technical"},
    {"id": "tech_stack_breadth", "name": "Technical breadth", "category": "Technical"},
    {"id": "tech_cloud", "name": "Cloud infrastructure experience", "category": "Technical"},
    {"id": "tech_devops", "name": "DevOps maturity signals", "category": "Technical"},
    {"id": "tech_security_tooling", "name": "Security tooling signals", "category": "Technical"},

    {"id": "market_services", "name": "Service offering clarity", "category": "Market"},
    {"id": "market_industry_focus", "name": "Industry focus clarity", "category": "Market"},
    {"id": "market_outsourcing_specialization", "name": "Outsourcing specialization", "category": "Market"},
    {"id": "market_engagement_models", "name": "Engagement model options", "category": "Market"},
    {"id": "market_pricing_transparency", "name": "Pricing transparency", "category": "Market"},
    {"id": "market_timezone_fit", "name": "Timezone or geo fit", "category": "Market"},

    {"id": "reputation_case_studies", "name": "Case studies or portfolio", "category": "Reputation"},
    {"id": "reputation_clients_named", "name": "Named clients or logos", "category": "Reputation"},
    {"id": "reputation_reviews_presence", "name": "Public reviews presence", "category": "Reputation"},
    {"id": "reputation_reviews_sentiment", "name": "Review sentiment signals", "category": "Reputation"},
    {"id": "reputation_press", "name": "Press mentions", "category": "Reputation"},
    {"id": "reputation_awards", "name": "Awards or recognition", "category": "Reputation"},

    {"id": "compliance_certifications", "name": "Security or compliance certifications", "category": "Compliance"},
    {"id": "compliance_security_policy", "name": "Security policy visibility", "category": "Compliance"},
    {"id": "compliance_privacy_policy", "name": "Privacy policy visibility", "category": "Compliance"},
    {"id": "compliance_data_protection", "name": "Data protection statements", "category": "Compliance"},
    {"id": "compliance_ip_protection", "name": "IP or NDA handling", "category": "Compliance"},

    {"id": "operations_methodology", "name": "Delivery methodology", "category": "Operations"},
    {"id": "operations_communication", "name": "Communication practices", "category": "Operations"},
    {"id": "operations_sla", "name": "SLA or response commitments", "category": "Operations"},
    {"id": "operations_onboarding", "name": "Onboarding process clarity", "category": "Operations"},

    {"id": "communication_english", "name": "English support", "category": "Communication"},

    {"id": "stability_financial_signals", "name": "Financial stability signals", "category": "Stability"},
    {"id": "stability_revenue_signals", "name": "Revenue range signals", "category": "Stability"},
    {"id": "stability_client_retention", "name": "Client retention signals", "category": "Stability"},

    {"id": "finance_rate_range", "name": "Rate range visibility", "category": "Finance"},
    {"id": "finance_payment_terms", "name": "Payment terms clarity", "category": "Finance"},

    {"id": "talent_seniority_mix", "name": "Seniority mix signals", "category": "Talent"},
    {"id": "talent_training", "name": "Training or certification programs", "category": "Talent"},

    {"id": "risk_legal", "name": "Legal disputes or negative news", "category": "Risk"},
    {"id": "risk_inconsistencies", "name": "Inconsistencies across sources", "category": "Risk"},
    {"id": "risk_generic_content", "name": "Overly generic or thin content", "category": "Risk"},
]


def _build_prompt(text: str, criteria_list: List[Dict[str, str]]) -> Tuple[str, str]:
    criteria = "\n".join(
        [f"- {item['id']} | {item['category']} | {item['name']}" for item in criteria_list]
    )
    system = (
        "You are a strict analyst scoring outsourcing vendors. "
        "Use ONLY the provided text. Do not assume or invent. "
        "If evidence is missing, score low and reduce coverage/confidence. "
        "Return ONLY valid JSON."
    )
    user = (
        "Score the company using the criteria list below. Use float scores.\n\n"
        "Criteria (score 0-5 each, 5 is best; weight 0.5-3.0):\n"
        f"{criteria}\n\n"
        "Return JSON in this schema:\n"
        "{\n"
        "  \"overall_score\": float (0-100),\n"
        "  \"coverage\": float (0-1),\n"
        "  \"confidence\": float (0-1),\n"
        "  \"category_scores\": {\"Category\": float (0-100), ...},\n"
        "  \"criteria\": [\n"
        "    {\"id\": string, \"name\": string, \"category\": string, \"score\": float (0-5), "
        "\"max_score\": 5.0, \"weight\": float, \"rationale\": string}\n"
        "  ],\n"
        "  \"flags\": [string],\n"
        "  \"has_public_info\": bool,\n"
        "  \"english_support\": \"yes\"|\"no\"|\"unknown\"\n"
        "}\n\n"
        "Only include criteria that are listed above. Do not add new criteria.\n\n"
        "If there is not enough public information, set has_public_info=false, "
        "overall_score=0, coverage=0, confidence=0, and include flag \"No public information found.\"\n\n"
        f"Text:\n{text}"
    )
    return system, user


def score_with_llm(
    pages: List[Tuple[str, str]],
    api_key: str,
    model: str,
    criteria_list: Optional[List[Dict[str, str]]] = None,
) -> Optional[Scorecard]:
    if not api_key:
        return None

    client = OpenAI(api_key=api_key)
    chunks: List[str] = []
    for url, html in pages:
        text = html_to_text(html)
        text = text[:4000]
        chunks.append(f"URL: {url}\n{text}")
    joined = "\n\n".join(chunks)
    joined = joined[:16000]

    if criteria_list is None:
        criteria_list = DEFAULT_CRITERIA
    if not criteria_list:
        return None

    system, user = _build_prompt(joined, criteria_list)

    try:
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0,
        )
    except Exception:
        return None

    raw = response.output_text or "{}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None

    def to_float(value: object, default: float = 0.0) -> float:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.strip().replace("%", "")
            try:
                return float(cleaned)
            except ValueError:
                return default
        return default

    criteria_list = []
    for item in data.get("criteria", []):
        try:
            criteria_list.append(
                CriterionScore(
                    criterion_id=item.get("id", "unknown"),
                    name=item.get("name", ""),
                    category=item.get("category", ""),
                    score=to_float(item.get("score", 0.0)),
                    max_score=to_float(item.get("max_score", 5.0), default=5.0),
                    weight=to_float(item.get("weight", 1.0), default=1.0),
                    rationale=item.get("rationale", ""),
                )
            )
        except (TypeError, ValueError):
            continue

    flags = list(data.get("flags") or [])
    has_public_info = data.get("has_public_info")
    english_support = str(data.get("english_support", "unknown")).lower()

    if has_public_info is False and "No public information found." not in flags:
        flags.append("No public information found.")

    if english_support == "no" and "No English support." not in flags:
        flags.append("No English support.")

    overall_score = to_float(data.get("overall_score", 0.0))
    coverage = to_float(data.get("coverage", 0.0))
    confidence = to_float(data.get("confidence", 0.0))
    category_scores = {
        key: to_float(value) for key, value in (data.get("category_scores") or {}).items()
    }

    if has_public_info is False:
        overall_score = 0.0
        coverage = 0.0
        confidence = 0.0
        category_scores = {}
        criteria_list = []

    return Scorecard(
        overall_score=overall_score,
        coverage=coverage,
        confidence=confidence,
        category_scores=category_scores,
        criteria=criteria_list,
        flags=flags,
    )
