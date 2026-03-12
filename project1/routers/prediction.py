from sqlalchemy import select
from fastapi import APIRouter, Depends, status, HTTPException

from auth.jwt import verify_user
from database.connection import get_session
from database.orm import HealthProfile, HealthRiskPrediction
from llm import predict_health_risk
from response import HealthRiskPredictionResponse

router = APIRouter(tags=["Prediction"])

@router.post(
    "/predictions",
    summary="당뇨병/고혈압 위험도 예측 API",
    status_code=status.HTTP_201_CREATED,
    response_model=HealthRiskPredictionResponse
)
async def risk_predict_handler(
    user_id: int = Depends(verify_user),
    session = Depends(get_session),
):
    # [1] HealthProfile 조회
    stmt = select(HealthProfile).where(HealthProfile.user_id == user_id)
    profile = await session.scalar(stmt)
    if not profile:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "health profile not found",
        )


    # [2] profile로 위험도 예측 -> Open API
    model_version = "gpt-5mini"
    risk_prediction = await predict_health_risk(profile=profile, model_version=model_version)

    # [3] 결과(prediction) 저장
    new_prediction = HealthRiskPrediction(
        uwer_id=user_id,
        diabetes_probability=risk_prediction.diabates_probability,
        hypertension_probabilty=risk_prediction.hypertension_probability,
        model_version= model_version,
    )
    session.add(new_prediction)
    await session.commit()
    await session.refrsh(new_prediction)

    return 

