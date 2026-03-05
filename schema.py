# schema.py — 데이터의 "모양"을 정의하는 파일

from pydantic import BaseModel

# ① TodoCreateRequest — 할 일을 "추가"할 때 받는 데이터

class TodoCreateRequest(BaseModel):
    title: str

#  ② TodoUpdateRequest — 할 일을 "수정"할 때 받는 데이터

class TodoUpdateRequest(BaseModel):
    is_done: bool  # True = 완료 / False = 미완료

# ③ TodoResponse — 응답할 때 "내보내는" 데이터

class TodoResponse(BaseModel):
    id : int
    title: str
    is_done: bool