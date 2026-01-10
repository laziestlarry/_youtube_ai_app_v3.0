from sqlalchemy.orm import Session

from app.db import models


def compute_scores_for_assessment(db: Session, assessment_id: int) -> models.Assessment | None:
    assessment = (
        db.query(models.Assessment)
        .filter(models.Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        return None

    db.query(models.DimensionScore).filter(
        models.DimensionScore.assessment_id == assessment_id
    ).delete()

    dimensions = db.query(models.Dimension).all()
    total_weighted = 0.0
    total_weight = 0.0

    for dimension in dimensions:
        dimension_answers = [
            answer
            for answer in assessment.answers
            if answer.question.dimension_id == dimension.id
            and answer.numeric_value is not None
        ]
        if not dimension_answers:
            continue

        numerator = 0.0
        denominator = 0.0
        for answer in dimension_answers:
            weight = answer.question.weight or 1.0
            numerator += answer.numeric_value * weight
            denominator += weight

        if denominator == 0:
            continue

        score = (numerator / denominator) * 100.0
        if score < 50:
            level = "L1"
        elif score < 70:
            level = "L2"
        else:
            level = "L3"

        dimension_score = models.DimensionScore(
            assessment_id=assessment.id,
            dimension_id=dimension.id,
            score=score,
            level=level,
        )
        db.add(dimension_score)
        total_weighted += score * (dimension.weight or 1.0)
        total_weight += dimension.weight or 1.0

    overall_score = total_weighted / total_weight if total_weight > 0 else 0.0
    assessment.overall_score = overall_score

    if overall_score < 50:
        readiness_level = "Foundation"
    elif overall_score < 65:
        readiness_level = "Bronze potential"
    elif overall_score < 80:
        readiness_level = "Silver potential"
    else:
        readiness_level = "Gold potential"

    assessment.readiness_level = readiness_level
    assessment.status = "completed"

    db.commit()
    db.refresh(assessment)
    return assessment
