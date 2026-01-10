from typing import List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

from app.db import models
from app.db.session import SessionLocal
from app.schemas.assessment import AssessmentCreate, AssessmentOut, AnswerCreate
from app.services.scoring import compute_scores_for_assessment

from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentOut,
    AnswerCreate,
    AssessmentReportOut,
)
from app.services.scoring import compute_scores_for_assessment
from app.services.reporting import build_guidance_for_assessment

router = APIRouter(prefix="/assessments", tags=["assessments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=AssessmentOut)
def create_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    organization = (
        db.query(models.Organization)
        .filter(models.Organization.name == payload.organization_name)
        .first()
    )
    if not organization:
        organization = models.Organization(name=payload.organization_name)
        db.add(organization)
        db.commit()
        db.refresh(organization)

    assessment = models.Assessment(
        organization_id=organization.id,
        status="in_progress",
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return AssessmentOut(
        id=assessment.id,
        organization_name=organization.name,
        status=assessment.status,
        overall_score=assessment.overall_score,
        readiness_level=assessment.readiness_level,
        dimension_scores=[],
    )


@router.post("/{assessment_id}/answers")
def submit_answers(
    assessment_id: int, answers: List[AnswerCreate], db: Session = Depends(get_db)
):
    assessment = (
        db.query(models.Assessment)
        .filter(models.Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    for payload in answers:
        question = (
            db.query(models.Question)
            .filter(models.Question.id == payload.question_id)
            .first()
        )
        if not question:
            continue

        answer = models.Answer(
            assessment_id=assessment_id,
            question_id=payload.question_id,
            numeric_value=payload.numeric_value,
            raw_value=payload.raw_value,
        )
        db.add(answer)
    db.commit()

    return {"status": "answers_saved"}


@router.post("/{assessment_id}/submit", response_model=AssessmentOut)
def complete_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = compute_scores_for_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    dimension_scores = [
        {
            "dimension_id": score.dimension_id,
            "dimension_code": score.dimension.code,
            "dimension_name": score.dimension.name,
            "score": score.score,
            "level": score.level,
        }
        for score in assessment.dimension_scores
    ]

    return AssessmentOut(
        id=assessment.id,
        organization_name=assessment.organization.name,
        status=assessment.status,
        overall_score=assessment.overall_score,
        readiness_level=assessment.readiness_level,
        dimension_scores=dimension_scores,
    )


@router.get("/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = (
        db.query(models.Assessment)
        .filter(models.Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    dimension_scores = [
        {
            "dimension_id": score.dimension_id,
            "dimension_code": score.dimension.code,
            "dimension_name": score.dimension.name,
            "score": score.score,
            "level": score.level,
        }
        for score in assessment.dimension_scores
    ]

    return AssessmentOut(
        id=assessment.id,
        organization_name=assessment.organization.name,
        status=assessment.status,
        overall_score=assessment.overall_score,
        readiness_level=assessment.readiness_level,
        dimension_scores=dimension_scores,
    )

@router.get("/{assessment_id}/report", response_model=AssessmentReportOut)
def get_assessment_report(assessment_id: int, db: Session = Depends(get_db)):
    assessment = (
        db.query(models.Assessment)
        .filter(models.Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Ensure scores exist
    if assessment.status != "completed" or not assessment.dimension_scores:
        assessment = compute_scores_for_assessment(db, assessment_id)
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found after scoring")

    guidance = build_guidance_for_assessment(db, assessment_id)
    if not guidance:
        raise HTTPException(status_code=500, detail="Could not generate guidance")

    # Build dimension_scores list as in get_assessment
    dimension_scores = [
        {
            "dimension_id": score.dimension_id,
            "dimension_code": score.dimension.code,
            "dimension_name": score.dimension.name,
            "score": score.score,
            "level": score.level,
        }
        for score in assessment.dimension_scores
    ]

    assessment_out = AssessmentOut(
        id=assessment.id,
        organization_name=assessment.organization.name,
        status=assessment.status,
        overall_score=assessment.overall_score,
        readiness_level=assessment.readiness_level,
        dimension_scores=dimension_scores,
    )

    return AssessmentReportOut(
        assessment=assessment_out,
        summary=guidance["summary"],
        strengths=guidance["strengths"],
        focus_areas=guidance["focus_areas"],
        next_90_days=guidance["next_90_days"],
        recommended_offers=guidance["recommended_offers"],
    )

@router.get("/{assessment_id}/report_html", response_class=HTMLResponse)
def get_assessment_report_html(
    assessment_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    assessment = (
        db.query(models.Assessment)
        .filter(models.Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Ensure scores exist
    if assessment.status != "completed" or not assessment.dimension_scores:
        assessment = compute_scores_for_assessment(db, assessment_id)
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found after scoring")

    guidance = build_guidance_for_assessment(db, assessment_id)
    if not guidance:
        raise HTTPException(status_code=500, detail="Could not generate guidance")

    dim_scores = sorted(
        assessment.dimension_scores,
        key=lambda d: d.score,
        reverse=True,
    )

    # Weakest dimension for simple Larry involvement plan
    weakest = dim_scores[-1]
    weakest_code = weakest.dimension.code
    weakest_name = weakest.dimension.name
    weakest_band = weakest.level

    larry_plan = {
        "title": "Larry CoPilot – Starter Involvement Plan",
        "dimension_name": weakest_name,
        "dimension_code": weakest_code,
        "dimension_level": weakest_band,
        "bullets": [
            f"Daily summary of issues and activity related to {weakest_name}.",
            "Draft responses for repetitive questions and tasks to reduce manual workload.",
            "Weekly short recap against your 90-day TekraQual priorities.",
        ],
    }

    return templates.TemplateResponse(
        "assessment_report.html",
        {
            "request": request,
            "assessment": assessment,
            "dimension_scores": dim_scores,
            "guidance": guidance,
            "larry_plan": larry_plan,
        },
    )
