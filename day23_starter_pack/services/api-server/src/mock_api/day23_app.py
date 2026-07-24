from __future__ import annotations
from fastapi import HTTPException,status
from day22_app import app
from schemas.uc2_schema import UC2AssessmentRequest,UC2QuantitativeAssessment
from services.longitudinal_service import build_assessment

ASSESSMENTS: dict[str,UC2QuantitativeAssessment]={}

@app.post('/v1/uc2/assessments',response_model=UC2QuantitativeAssessment,status_code=status.HTTP_201_CREATED)
def create_assessment(body:UC2AssessmentRequest)->UC2QuantitativeAssessment:
    item=build_assessment(body.scenarioId); ASSESSMENTS[item.assessmentId]=item; return item

@app.get('/v1/uc2/assessments/{assessment_id}',response_model=UC2QuantitativeAssessment)
def get_assessment(assessment_id:str)->UC2QuantitativeAssessment:
    if assessment_id not in ASSESSMENTS: raise HTTPException(404,'ASSESSMENT_NOT_FOUND')
    return ASSESSMENTS[assessment_id]
