from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey,Integer, Float, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False,
    )

class HealthProfile(Base):
    __tablename__= "health_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)

    age: Mapped[int] = mapped_column(Integer)
    height_cm: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    smoking: Mapped[bool] = mapped_column(Boolean)
    exercise_per_week: Mapped[int] = mapped_column(Integer)

class HealthRiskPrediction(Base):
    __tablename__ = "health_risk_prediction"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # 당뇨병 위험도 / 고혈압 위험도
    diabetes_probability: Mapped[float] = mapped_column(Float)
    hypertension_probability:Mapped[float] = mapped_column(Float)

    modl_version: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

