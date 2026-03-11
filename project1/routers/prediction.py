from sqlalchemy import select
from fastapi import APIRouter, Depends, status, HTTPException

from auth.jwt import verify_user
from database.connection import get_session
from database.orm import HealthProfile

router = APIRouter(tags=["Prediction"])

@router.post(
    "/predictions",
    summary="당뇨병/고혈압 위험도 예측 API",
    status_code=status.HTTP_201_CREATED,
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
    # [3] 결과(prediction) 저장
    return 

