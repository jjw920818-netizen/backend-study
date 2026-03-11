from pydantic import BaseModel

# 회원가입 요청 본문(Request Body) 데이터 형태
class UserSignUpRequest(BaseModel):
    name: str # 필수값(required)
    age: int  # 필수값(required)

# 회원가입 응답 본문(Response Body)의 데이터 형태
class UserSignUpResponse(BaseModel):
    id: int
    name: str
    age: int | None
