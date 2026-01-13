from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    size_bracket = Column(String, nullable=True)

    assessments = relationship("Assessment", back_populates="organization")


class Dimension(Base):
    __tablename__ = "dimensions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    weight = Column(Float, default=1.0)

    questions = relationship("Question", back_populates="dimension")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    dimension_id = Column(Integer, ForeignKey("dimensions.id"))
    text = Column(String, nullable=False)
    type = Column(String, default="likert_1_5")
    weight = Column(Float, default=1.0)

    dimension = relationship("Dimension", back_populates="questions")
    answers = relationship("Answer", back_populates="question")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="in_progress")
    overall_score = Column(Float, nullable=True)
    readiness_level = Column(String, nullable=True)

    organization = relationship("Organization", back_populates="assessments")
    answers = relationship("Answer", back_populates="assessment")
    dimension_scores = relationship("DimensionScore", back_populates="assessment")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    numeric_value = Column(Float, nullable=True)
    raw_value = Column(String, nullable=True)

    assessment = relationship("Assessment", back_populates="answers")
    question = relationship("Question", back_populates="answers")


class DimensionScore(Base):
    __tablename__ = "dimension_scores"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    dimension_id = Column(Integer, ForeignKey("dimensions.id"))
    score = Column(Float, nullable=False)
    level = Column(String, nullable=True)

    assessment = relationship("Assessment", back_populates="dimension_scores")
    dimension = relationship("Dimension")
