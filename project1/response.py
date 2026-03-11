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