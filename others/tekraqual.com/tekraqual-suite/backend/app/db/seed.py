from app.db import models
from app.db.session import SessionLocal


def ensure_seed_data():
    db = SessionLocal()
    try:
        if db.query(models.Dimension).count() == 0:
            dimensions = [
                models.Dimension(id=1, code="OPS", name="Operational Excellence", description="Processes, SLAs, automation & reliability.", weight=1.2),
                models.Dimension(id=2, code="CX", name="Customer & Experience", description="Customer satisfaction, retention, response quality.", weight=1.1),
                models.Dimension(id=3, code="GOV", name="Governance & Risk", description="Roles, responsibilities, controls, risk handling.", weight=1.1),
                models.Dimension(id=4, code="DATA", name="Data & Insight", description="Data quality, dashboards, decision support.", weight=1.0),
                models.Dimension(id=5, code="INCOME", name="Income & Scalability", description="Revenue model clarity and scalability readiness.", weight=1.0),
            ]
            db.add_all(dimensions)
            db.commit()

        if db.query(models.Question).count() == 0:
            code_to_id = {d.code: d.id for d in db.query(models.Dimension).all()}
            questions = [
                models.Question(
                    id=1,
                    dimension_id=code_to_id.get("OPS"),
                    text="We have documented processes for key operations.",
                    type="likert_1_5",
                    weight=1.0,
                ),
                models.Question(
                    id=2,
                    dimension_id=code_to_id.get("CX"),
                    text="We regularly measure customer satisfaction (NPS/CSAT).",
                    type="likert_1_5",
                    weight=1.0,
                ),
                models.Question(
                    id=3,
                    dimension_id=code_to_id.get("DATA"),
                    text="We track key KPIs with up-to-date dashboards.",
                    type="likert_1_5",
                    weight=1.0,
                ),
                models.Question(
                    id=4,
                    dimension_id=code_to_id.get("GOV"),
                    text="Roles & responsibilities for decisions are clearly defined.",
                    type="likert_1_5",
                    weight=1.0,
                ),
            ]
            db.add_all(questions)
            db.commit()
    finally:
        db.close()
