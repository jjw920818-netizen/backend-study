from datetime import datetime
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    email: str 
    created_at: datetime

class LogInResponse(BaseModel):
    access_token: str


class HealthProfileResponse(BaseModel):
    id: int
    user_id: int
    age: int
    height_cm: float
    weight_kg: float
    smoking: bool
    exercise_per_week: int

class HealthRiskPredictionResponse(BaseModel):
    id: int
    user_id: int
    diabates_probability: float
    hypertension_probability: float
    # model_version -> 클라이언트에게 공개하지 않을 수 있음
    created_at: datetime