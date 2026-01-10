from typing import List, Dict
from sqlalchemy.orm import Session

from app.db import models


def _band_for_score(score: float) -> str:
    """Map numeric score (0–100) to a human-readable band."""
    if score < 50:
        return "Foundation"
    elif score < 65:
        return "Defined"
    elif score < 80:
        return "Managed"
    else:
        return "Optimized"


def _dimension_label(code: str) -> str:
    """Map dimension code to a human-readable label."""
    mapping = {
        "OPS": "Operational Excellence",
        "CX": "Customer & Experience",
        "GOV": "Governance & Risk",
        "DATA": "Data & Insight",
        "INCOME": "Income & Scalability",
    }
    return mapping.get(code, code)


def _dimension_narrative(code: str, score: float) -> str:
    """Return a short narrative for a given dimension score."""
    band = _band_for_score(score)
    label = _dimension_label(code)

    if code == "OPS":
        if band == "Foundation":
            return (
                f"{label}: Work is mostly ad hoc. Start by documenting 3–5 core "
                "processes and assigning clear owners."
            )
        if band == "Defined":
            return (
                f"{label}: You have key processes identified but uneven adherence. "
                "Focus on standardizing how work is actually done."
            )
        if band == "Managed":
            return (
                f"{label}: Processes are stable and measured. Next step is targeted "
                "automation and continuous improvement cycles."
            )
        return (
            f"{label}: Operations are robust. Use this as the backbone for scaling "
            "and more advanced AI/automation."
        )

    if code == "CX":
        if band == "Foundation":
            return (
                f"{label}: Customer experience is inconsistent and under-measured. "
                "Start tracking response times and basic satisfaction."
            )
        if band == "Defined":
            return (
                f"{label}: Basic CX metrics exist. Work on closing gaps across channels "
                "and teams."
            )
        if band == "Managed":
            return (
                f"{label}: CX is tracked and acted on. Next step is proactive outreach "
                "and experience design."
            )
        return (
            f"{label}: CX is a clear strength. You can use it as a differentiator in "
            "sales and investor conversations."
        )

    if code == "GOV":
        if band == "Foundation":
            return (
                f"{label}: Roles, responsibilities, and policies are unclear. Put a "
                "simple governance and risk framework in place."
            )
        if band == "Defined":
            return (
                f"{label}: Core roles and some policies exist. Focus on making risk and "
                "change management explicit and visible."
            )
        if band == "Managed":
            return (
                f"{label}: Governance is working. Next step is embedding it into regular "
                "reviews and decision routines."
            )
        return (
            f"{label}: Governance is mature. Leverage this strength when negotiating "
            "partnerships and deals."
        )

    if code == "DATA":
        if band == "Foundation":
            return (
                f"{label}: Data is fragmented and trust is low. Start by defining 5–10 "
                "core KPIs and stabilizing how they are reported."
            )
        if band == "Defined":
            return (
                f"{label}: Key reports exist but are manual. Prioritize automating data "
                "flows and improving quality."
            )
        if band == "Managed":
            return (
                f"{label}: Dashboards are reliable. Next step is deeper insight, "
                "segmentation and forecasting."
            )
        return (
            f"{label}: Data is a strategic asset. You can now safely build more advanced "
            "analytics and AI on top."
        )

    if code == "INCOME":
        if band == "Foundation":
            return (
                f"{label}: Revenue model is fragile or unclear. Clarify your main revenue "
                "streams and basic unit economics."
            )
        if band == "Defined":
            return (
                f"{label}: Revenue model is defined. Focus on proving scalability without "
                "breaking operations."
            )
        if band == "Managed":
            return (
                f"{label}: Income and margins are well understood. Next step is testing "
                "new growth levers in a controlled way."
            )
        return (
            f"{label}: Income model is highly scalable. Combine this with strong governance "
            "to support funding and expansion."
        )

    # Fallback
    return f"{label}: Score {round(score)} – review this area in more detail."


def build_guidance_for_assessment(db: Session, assessment_id: int) -> Dict:
    """
    Build a human-readable guidance structure for an assessment.

    Returns a dict with:
      - summary
      - strengths[]
      - focus_areas[]
      - next_90_days[]
      - recommended_offers[]
    """
    assessment = (
        db.query(models.Assessment)
        .filter(models.Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        return {}

    # Ensure dimension scores exist (should already be computed by scoring service)
    if not assessment.dimension_scores:
        return {}

    dim_scores = sorted(
        assessment.dimension_scores,
        key=lambda d: d.score,
        reverse=True,
    )

    # Strengths: top 2 dimensions
    strengths: List[Dict] = []
    for ds in dim_scores[:2]:
        strengths.append(
            {
                "title": f"{_dimension_label(ds.dimension.code)} – Strength",
                "dimension_code": ds.dimension.code,
                "score": ds.score,
                "band": _band_for_score(ds.score),
                "body": _dimension_narrative(ds.dimension.code, ds.score),
            }
        )

    # Focus areas: bottom 2 dimensions
    focus_areas: List[Dict] = []
    for ds in dim_scores[-2:]:
        focus_areas.append(
            {
                "title": f"{_dimension_label(ds.dimension.code)} – Priority Focus",
                "dimension_code": ds.dimension.code,
                "score": ds.score,
                "band": _band_for_score(ds.score),
                "body": _dimension_narrative(ds.dimension.code, ds.score),
            }
        )

    overall = assessment.overall_score or 0.0
    level = assessment.readiness_level or "Foundation"

    if overall < 80:
        summary = (
            f"{assessment.organization.name} currently sits at {round(overall)}/100 "
            f"({level}) on the TekraQual Readiness scale. "
            "Core structures exist but there is still meaningful room to improve maturity, "
            "governance, and data for decisions."
        )
    else:
        summary = (
            f"{assessment.organization.name} shows a strong readiness score of "
            f"{round(overall)}/100 ({level}), with solid foundations across most dimensions."
        )

    # Use the weakest dimension to flavor the 90-day plan
    weakest = dim_scores[-1]
    weakest_label = _dimension_label(weakest.dimension.code)

    next_90_days = [
        {
            "title": "Define 3 concrete priorities",
            "body": (
                f"Choose 3 specific improvements that will move {weakest_label} "
                "one band up on the TekraQual scale."
            ),
        },
        {
            "title": "Assign clear owners & dates",
            "body": (
                "For each priority, assign an accountable owner and a realistic target date "
                "within the next 90 days."
            ),
        },
        {
            "title": "Review progress monthly",
            "body": (
                "Set a recurring monthly review using the TekraQual dimensions so improvement "
                "is visible and continuous."
            ),
        },
    ]

    recommended_offers = [
        {
            "title": "Larry CoPilot Setup + TekraQual Readiness Deep Dive",
            "body": (
                "Use the current results as a starting point to design concrete workflows and "
                "dashboards around your operations and governance."
            ),
        },
        {
            "title": "TekraQual Governance Starter Pack",
            "body": (
                "Adopt the templates (process maps, RACI, risk register, dashboards) to "
                "accelerate implementation."
            ),
        },
    ]

    return {
        "summary": summary,
        "strengths": strengths,
        "focus_areas": focus_areas,
        "next_90_days": next_90_days,
        "recommended_offers": recommended_offers,
    }
