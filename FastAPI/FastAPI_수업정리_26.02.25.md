# 🚀 FastAPI 수업 정리 3일차

> 작성일: 2026년 2월 26일
> 학습 내용: Request Body / Pydantic / Response Model / HTTPException / PATCH

---

## 📚 오늘 배운 것 한눈에 보기

| 주제 | 이전 수업 복습 | 오늘 새로 배운 것 |
|---|---|---|
| Path Parameter | ✅ 복습 | - |
| Query Parameter | ✅ 복습 | - |
| POST 요청 | ✅ 복습 | Request Body + Pydantic |
| 응답 | ✅ 복습 | Response Model |
| 에러 처리 | - | ✅ HTTPException |
| 수정 API | - | ✅ PATCH |
| 파일 분리 | - | ✅ schema.py |

---

## 1. 파일 구조 (새로운 개념!) ⭐

```
📁 프로젝트 폴더
├── main.py      ← API 엔드포인트 (라우터) 정의
└── schema.py    ← 데이터 형태(모양) 정의
```

### 왜 파일을 나눌까?

```python
# main.py 에서 schema.py 불러오기
from schema import UserSignUpRequest, UserResponse, UserUpdateRequest
```

> 💡 코드가 길어질수록 한 파일에 다 넣으면 복잡해짐
> 역할에 따라 파일을 나누는 것이 **좋은 코드 습관**
> - `main.py` → "어떤 URL로 요청받을지" 담당
> - `schema.py` → "데이터가 어떻게 생겼는지" 담당

---

## 2. 이전 수업 복습 (main.py 앞부분)

### 전체 사용자 조회

```python
@app.get("/users")
def get_users_handler():
    return users
```

### Query Parameter로 회원 검색

```python
@app.get("/users/search")
def search_user_handler(
    name: str = Query(..., min_length=2),  # 필수값, 최소 2글자
    age: int = Query(None, ge=1),          # 선택값, 1 이상
):
    return {"id": 0, "name": name, "age": age}
```

### Path Parameter로 단일 사용자 조회

```python
@app.get("/users/{user_id}")
def get_first_handler(
    user_id: int = Path(..., ge=1, description="사용자의 ID"),
    field: str = Query(None, description="출력할 필드 선택(id 또는 name)"),
):
    user = users[user_id - 1]
    if field in ("id", "name"):
        return user[field]
    return user
```

> ✅ 이 세 가지는 이전 수업에서 배운 내용

---

## 3. Pydantic & Schema (오늘의 핵심 1!) ⭐

### Pydantic이란?

**데이터의 형태(모양)를 정의하고 자동으로 검증해주는 라이브러리**
오늘 배운 Class 개념이 여기서 본격적으로 사용

```python
# schema.py
from pydantic import BaseModel
```

`BaseModel`을 **상속**받으면 Pydantic의 검증 기능을 모두 사용할 수 있음

> 💡 **상속이란?**
> 부모 클래스의 기능을 그대로 물려받는 것
> `class UserSignUpRequest(BaseModel):` 에서
> `(BaseModel)` 이 "BaseModel의 기능을 물려받겠다"는 의미

---

### schema.py 전체 설명

```python
from pydantic import BaseModel

# ① 회원가입 요청 데이터 형태
class UserSignUpRequest(BaseModel):
    name: str           # 필수값 (반드시 있어야 함)
    age: int | None = None  # 선택값 (없으면 None)

# ② 응답 데이터 형태
class UserResponse(BaseModel):
    id: int
    name: str
    age: int | None

# ③ 사용자 정보 수정 요청 데이터 형태
class UserUpdateRequest(BaseModel):
    name: str | None = None  # 선택적
    age: int | None = None   # 선택적
```

#### 세 가지 클래스의 역할

| 클래스 | 역할 | 사용되는 곳 |
|---|---|---|
| `UserSignUpRequest` | 회원가입할 때 받는 데이터 형태 | POST `/users/sign-up` |
| `UserResponse` | 응답으로 내보낼 데이터 형태 | 모든 응답 |
| `UserUpdateRequest` | 수정할 때 받는 데이터 형태 | PATCH `/users/{user_id}` |

---

#### 필수값 vs 선택값

```python
name: str              # 필수값 → 없으면 에러!
age: int | None = None # 선택값 → 없으면 None으로 처리
```

| 표현 | 의미 |
|---|---|
| `name: str` | 반드시 있어야 하는 값 |
| `age: int \| None = None` | 있어도 되고 없어도 되는 값 |

---

## 4. Request Body (오늘의 핵심 2!) ⭐

### Request Body란?

POST/PATCH 요청할 때 URL이 아닌 **요청의 몸통(Body)에 데이터를 담아서 보내는 것**

```
❌ URL에 담으면 (위험!)
POST /users/sign-up?name=Alice&age=20&password=1234  ← 비밀번호 노출!

✅ Body에 담으면 (안전!)
POST /users/sign-up
Body: {
    "name": "Alice",
    "age": 20,
    "password": "1234"   ← URL에 안 보임!
}
```

---

### 회원가입 API 전체 코드

```python
@app.post("/users/sign-up",
    status_code=status.HTTP_201_CREATED,  # 성공 시 201 반환
    response_model=UserResponse,          # 응답 형태 지정
)
def sign_up_handler(body: UserSignUpRequest):
    new_user = {
        "id": len(users) + 1,
        "name": body.name,
        "age": body.age,
    }
    users.append(new_user)
    return new_user
```

#### 코드 한 줄씩 설명

```python
def sign_up_handler(body: UserSignUpRequest):
#                   ^^^^  ^^^^^^^^^^^^^^^^
#                   변수명  타입힌트 (Pydantic 모델)
```

매개변수의 타입힌트가 `BaseModel`을 상속받은 클래스이면,
FastAPI가 자동으로 **Request Body에서 데이터를 꺼내옴!**

```python
body.name  # Body에서 name 값 가져오기
body.age   # Body에서 age 값 가져오기
```

---

## 5. Response Model (오늘의 핵심 3!) ⭐

### Response Model이란?

**응답으로 내보낼 데이터의 형태를 지정하는 것**

```python
@app.post("/users/sign-up",
    response_model=UserResponse,  # ← 이게 Response Model
)
```

### 왜 필요할까?

```python
new_user = {
    "id": 1,
    "name": "Alice",
    "age": 20,
    "grade": "special"  # ← 실수로 추가된 민감한 데이터
}
return new_user
```

`response_model=UserResponse`를 지정하면:

```python
# UserResponse에 없는 "grade"는 자동으로 제거됨!
# 실제 응답: {"id": 1, "name": "Alice", "age": 20}
```

#### Response Model의 3가지 역할

| 역할 | 설명 |
|---|---|
| **데이터 검증** | 응답 데이터가 올바른 형식인지 확인 |
| **필드 필터링** | 노출되면 안 되는 값 자동 제거 |
| **문서화** | `/docs`에 예상 응답 형태 자동 표시 |

---

## 6. status_code (HTTP 상태 코드)

```python
@app.post("/users/sign-up",
    status_code=status.HTTP_201_CREATED,  # 201
)
```

요청이 성공했을 때 어떤 숫자 코드를 반환할지 지정

| 코드 | 의미 | 언제 쓰나 |
|---|---|---|
| `200 OK` | 성공 | 조회, 수정 성공 |
| `201 Created` | 생성 성공 | 회원가입, 새 데이터 생성 |
| `400 Bad Request` | 잘못된 요청 | 데이터 형식 오류 |
| `404 Not Found` | 찾을 수 없음 | 존재하지 않는 사용자 |

---

## 7. HTTPException - 에러 처리 (오늘의 핵심 4!) ⭐

### HTTPException이란?

**조건에 맞지 않을 때 직접 에러를 발생시키는 것**

```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="존재하지 않는 사용자의 ID입니다",
)
```

> 💡 **`raise`란?**
> "이 에러를 일부러 발생시켜라!" 라는 파이썬 문법

### PATCH API에서 에러 처리 예시

```python
# 1-a. 존재하지 않는 user_id인지 확인
if user_id > len(users):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="존재하지 않는 사용자의 ID입니다",
    )

# 1-b. 수정할 데이터가 아무것도 없는지 확인
if body.name is None and body.age is None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="수정할 데이터가 없습니다",
    )
```

---

## 8. PATCH - 사용자 정보 수정 API (오늘의 핵심 5!) ⭐

### PUT vs PATCH 차이

| | PUT | PATCH |
|---|---|---|
| **의미** | 전체 교체 | 일부만 수정 |
| **예시** | name, age 둘 다 바꿔야 함 | name만 또는 age만 바꿔도 됨 |

### PATCH API 전체 코드

```python
@app.patch("/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
def update_user_handler(
    user_id: int = Path(..., ge=1),
    body: UserUpdateRequest = Body(...),
):
    # 1-a. user_id 검증
    if user_id > len(users):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 사용자의 ID입니다",
        )

    # 1-b. 수정할 데이터 검증
    if body.name is None and body.age is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 데이터가 없습니다",
        )

    # 2. 사용자 조회 & 수정
    user = users[user_id - 1]

    if body.name is not None:
        user["name"] = body.name

    if body.age is not None:
        user["age"] = body.age

    return user
```

### 동작 흐름

```
PATCH /users/2
Body: {"name": "Bob2"}
    │
    ├─ user_id = 2 → users[1] = {"id": 2, "name": "bob", "age": 30}
    │
    ├─ body.name = "Bob2" (있음) → user["name"] = "Bob2"  ✅ 수정
    ├─ body.age = None (없음)   → 수정 안 함
    │
    └─ return {"id": 2, "name": "Bob2", "age": 30}
```

### UserUpdateRequest가 선택값인 이유

```python
class UserUpdateRequest(BaseModel):
    name: str | None = None  # 선택적
    age: int | None = None   # 선택적
```

PATCH는 일부만 수정하는 요청이라 name만 보내도, age만 보내도 되기 때문

```
{"name": "Bob2"}           → name만 수정
{"age": 25}                → age만 수정
{"name": "Bob2", "age": 25} → 둘 다 수정 (이건 PUT과 같음)
```

---

## 9. Path / Query / Request Body 최종 비교

```
요청이 들어올 때 데이터를 전달하는 3가지 방법
```

|                  | Path Parameter | Query Parameter   | Request Body |

| **위치**          | URL 경로 안      | URL 뒤 `?`          | 요청 몸통 |
| **예시**          | `/users/1`     | `/users?name=Alex`  | `{"name": "Alex"}` |
| **주 용도**        | 리소스 **식별**  | 필터링, 검색           | 데이터 **전송** |
| **보안**          | URL에 노출      | URL에 노출            | URL에 노출 안 됨 ✅ |
| **FastAPI**      | `Path(...)`   | `Query(...)`         | Pydantic 모델 |
| **HTTP Method** | 주로 GET        | 주로 GET              | POST, PATCH, PUT |

---

## 10. 전체 코드 흐름 요약

```
클라이언트
    │
    │  POST /users/sign-up
    │  Body: {"name": "Alice", "age": 20}
    ▼
FastAPI 라우터
    │
    │  body: UserSignUpRequest 로 데이터 검증
    │  name=Alice (str) ✅
    │  age=20 (int) ✅
    ▼
sign_up_handler 실행
    │
    │  new_user 생성 & users에 추가
    ▼
Response Model (UserResponse) 필터링
    │
    │  id, name, age 만 남기고 나머지 제거
    ▼
클라이언트에게 응답
    {"id": 4, "name": "Alice", "age": 20}
```

---

## 11. 용어 정리

|       용어          |              설명                      |
| **Pydantic**       | 데이터 형태를 정의하고 자동 검증해주는 라이브러리 |
| **BaseModel**      | Pydantic의 기본 클래스, 상속받으면 검증 기능 사용 가능 |
| **상속**            | 부모 클래스의 기능을 물려받는 것 `class A(B):` |
| **Request Body**   | POST/PATCH 요청 시 URL이 아닌 몸통에 담는 데이터 |
| **Response Model** | 응답으로 내보낼 데이터 형태를 지정하는 것 |
| **HTTPException**  | 조건에 맞지 않을 때 직접 에러를 발생시키는 것 |
| **raise**          | 에러를 일부러 발생시키는 파이썬 문법 |
| **status_code**    | 요청 결과를 숫자로 나타내는 HTTP 상태 코드 |
| **PUT**            | 데이터 전체를 교체하는 HTTP 메서드 |
| **PATCH**          | 데이터 일부만 수정하는 HTTP 메서드 |
| **schema.py**      | 데이터 형태(모양)를 정의하는 파일 |



> 📌 **오늘 수업 핵심 한 줄 요약**
> Pydantic으로 데이터 형태를 정의하고, Request Body로 데이터를 안전하게 받고,
> Response Model로 응답을 필터링하며, HTTPException으로 에러를 직접 처리한다!
