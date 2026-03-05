# 🚀 FastAPI 수업 정리 2일차

> 작성일: 2026년 2월 24일
> 학습 내용: Path Parameter 심화 / Query Parameter / Type Hint / Class & Instance

---

## 📚 오늘 배운 것 한눈에 보기

| 주제 | 핵심 내용 |
|---|---|
| **Path Parameter 심화** | `Path()`로 유효성 검사 조건 추가 |
| **Query Parameter** | `?key=value` 형태로 부가 조건 전달 |
| **?field 선택** | 원하는 필드만 골라서 응답받기 |
| **Type Hint** | 변수/함수에 타입 명시하기 |
| **Class & Instance** | 객체를 찍어내는 설계도 개념 |

---

## 1. 새로 추가된 import

```python
from fastapi import FastAPI, Path, Query
```

| 이름 | 역할 |
|---|---|
| `FastAPI` | 앱 생성 |
| `Path` | Path Parameter에 유효성 검사 조건 추가 |
| `Query` | Query Parameter에 유효성 검사 조건 추가 |

---

## 2. Path Parameter 심화

### 기본 사용 (1일차 복습)

```python
@app.get("/users/{user_id}")
def get_user_handler(user_id: int):
    return users[user_id - 1]
```

### 유효성 검사 추가 ✅

```python
@app.get("/users/{user_id}")
def get_user_handler(
    user_id: int = Path(..., ge=1, description="user_id는 1 이상")
):
    return users[user_id - 1]
```

#### `Path()` 안에 들어가는 옵션들

| 옵션 | 의미 | 예시 |
|---|---|---|
| `...` | 필수값 (반드시 입력) | `Path(...)` |
| `ge` | 이상 (greater than or equal) | `ge=1` → 1 이상 |
| `gt` | 초과 (greater than) | `gt=0` → 0 초과 |
| `le` | 이하 (less than or equal) | `le=100` → 100 이하 |
| `lt` | 미만 (less than) | `lt=100` → 100 미만 |
| `max_length` | 최대 글자 수 | `max_length=6` |
| `description` | `/docs`에 표시될 설명 | `description="사용자 ID"` |

> 💡 **왜 유효성 검사가 필요할까?**
> `user_id`에 `-1`이나 `0`이 들어오면 `users[-2]`, `users[-1]`이 되어 엉뚱한 데이터가 반환돼요.
> `ge=1` 조건을 넣으면 1 미만의 값이 들어올 때 자동으로 **422 에러**를 반환합니다!

---

## 3. Query Parameter

### Query Parameter란?

URL에서 `?` 뒤에 `key=value` 형태로 붙는 값입니다.

```
http://127.0.0.1:8000/users/search?name=Alice
                                   ^^^^^^^^^^^
                                   Query Parameter
```

여러 개를 동시에 쓸 때는 `&`로 연결합니다.

```
/users/search?name=Alice&age=20
```

---

### 기본 사용

```python
@app.get("/users/search")
def search_user_handler(name: str):
    return {"name": name}
```

```
GET /users/search?name=Alice  →  {"name": "Alice"}
```

---

### 유효성 검사 추가 ✅

```python
@app.get("/users/search")
def search_user_handler(
    name: str = Query(..., min_length=2),   # 필수값, 최소 2글자
    age: int = Query(None, ge=1),           # 선택값, 1 이상
):
    return {"name": name, "age": age}
```

#### `Query()` 옵션들

| 옵션 | 의미 | 예시 |
|---|---|---|
| `...` | 필수값 (required) | `Query(...)` |
| `None` | 선택값 (optional) | `Query(None)` |
| `min_length` | 최소 글자 수 | `min_length=2` |
| `max_length` | 최대 글자 수 | `max_length=10` |
| `ge`, `gt`, `le`, `lt` | 숫자 범위 (Path와 동일) | `ge=1` |

```
GET /users/search?name=Al           → 에러! (2글자 미만)
GET /users/search?name=Alice        → {"name": "Alice", "age": null}
GET /users/search?name=Alice&age=20 → {"name": "Alice", "age": 20}
```

---

## 4. ?field로 원하는 필드만 선택하기 ⭐

### 개념

같은 사용자 데이터라도 원하는 필드만 골라서 받을 수 있습니다.

```
GET /users/1            → {"id": 1, "name": "Alice"}  (전체 반환)
GET /users/1?field=id   → ("id", 1)                   (id만 반환)
GET /users/1?field=name → ("name", "Alice")            (name만 반환)
```

### 코드

```python
@app.get("/users/{user_id}")
def get_user_handler(
    user_id: int = Path(..., ge=1, description="사용자의 ID"),
    field: str = Query(None, description="출력할 필드 선택 (id 또는 name)")
):
    user = users[user_id - 1]         # user_id에 해당하는 사용자 찾기
    if field in ("id", "name"):       # field가 "id" 또는 "name"이면
        return (field, user[field])   # 해당 필드만 반환
    return user                       # 아니면 전체 반환
```

### 동작 흐름

```
GET /users/2?field=name
    │
    ├─ user_id = 2  →  users[1]  =  {"id": 2, "name": "Bob"}
    ├─ field = "name"  →  "name" in ("id", "name")  →  True
    └─ return ("name", "Bob")

GET /users/2
    │
    ├─ user_id = 2  →  users[1]  =  {"id": 2, "name": "Bob"}
    ├─ field = None  →  None in ("id", "name")  →  False
    └─ return {"id": 2, "name": "Bob"}  (전체 반환)
```

---

## 5. Path Parameter vs Query Parameter 비교

| 구분 | Path Parameter | Query Parameter |
|---|---|---|
| **위치** | URL 경로 안 `/users/{user_id}` | URL 뒤 `?name=Alice` |
| **필수 여부** | 항상 필수 | 필수/선택 모두 가능 |
| **주 용도** | 특정 리소스 **식별** | 필터링, 검색, 정렬 등 **부가 조건** |
| **FastAPI 도구** | `Path(...)` | `Query(...)` |

---

## 6. POST 요청 - 회원가입 API

```python
@app.post("/users/sign-up")
def sign_up_user_handler(name: str):
    return {"msg": f"hello {name}"}
```

> 💡 **snake_case vs 하이픈(-)**
> - 파이썬 변수명/함수명 → `snake_case` (언더스코어): `sign_up_user_handler`
> - URL 경로 → `-` (하이픈): `/users/sign-up`

---

## 7. HTTP 메서드 정리

```
요청 = HTTP Method (동작) + URL (대상)
```

| Method | 의미 | 예시 |
|---|---|---|
| `GET` | 조회 | `GET /users/1` |
| `POST` | 생성 | `POST /users/sign-up` |
| `PUT` | 전체 수정 | `PUT /users/1` |
| `PATCH` | 일부 수정 | `PATCH /users/1` |
| `DELETE` | 삭제 | `DELETE /comments/10` |

---

## 8. Type Hint

### Type Hint란?

변수나 함수의 매개변수/반환값에 **데이터 타입을 명시**하는 것입니다.

```python
변수명: 타입 = 값
```

> 💡 Type Hint는 파이썬에서 강제가 아니에요.
> 틀린 타입을 넣어도 파이썬 자체에서는 에러가 안 납니다.
> 하지만 **FastAPI, Pydantic** 같은 라이브러리는 이걸 보고 실제로 검증합니다!

---

### 기본 타입

```python
name: str = "alex"        # 문자열
price: float = 10.5       # 소수
is_active: bool = True    # 참/거짓
age: int = 10             # 정수
```

| 타입 | 의미 | 예시 값 |
|---|---|---|
| `str` | 문자열 | `"alex"`, `"hello"` |
| `int` | 정수 | `1`, `10`, `100` |
| `float` | 소수 | `10.5`, `3.14` |
| `bool` | 참/거짓 | `True`, `False` |

---

### 여러 타입 허용 → `|` 사용

```python
score: int | float = 90     # int 또는 float
age: str | int = "10"       # str 또는 int
```

---

### 함수에서 Type Hint

```python
# Type Hint 없을 때 → 실행 전까지 에러를 모름
def add(num1, num2):
    return num1 + num2

add(1, "hello")  # 실행해야 에러 발생 ❌

# Type Hint 있을 때 → IDE에서 미리 경고해줌
def add(num1: int, num2: int) -> int:
    return num1 + num2
#                          ↑
#                    반환값 타입 (이 함수는 int를 반환)
```

---

### list / dict Type Hint

```python
# list
names: list[str] = ["alex", "bob", "chris"]
data: list[str | int | bool] = ["alex", 96, True]

# dict
scores: dict[str, int] = {"eng": 100, "math": 90}
#              ↑    ↑
#             key  value
scores: dict[str, int | bool] = {"eng": 100, "science": True}
```

---

### ⚠️ 주의: 내장 타입을 변수명으로 쓰면 안 돼요!

```python
# 잘못된 예시 ❌
names = list = ["alex", "bob", "chris"]  # list가 변수로 덮어씌워짐
list()  # TypeError! 함수로 못 씀

# 올바른 예시 ✅
names: list = ["alex", "bob", "chris"]
list()  # 정상 동작
```

> `list`, `dict`, `str`, `int` 같은 파이썬 내장 타입 이름을 변수명으로 쓰면
> 원래 기능이 덮어씌워져서 망가집니다!

---

## 9. Class와 Instance ⭐ (오늘의 핵심 개념!)

### 이해하기 어렵죠? 비유로 먼저 이해해봐요

> 🏠 **붕어빵 틀 = Class (클래스)**
> 🐟 **실제 붕어빵 = Instance (인스턴스)**

붕어빵 틀(Class)은 **설계도**입니다. 틀 자체는 먹을 수 없어요.
틀로 찍어낸 실제 붕어빵(Instance)이 **실체화된 객체**입니다.

---

### 코드로 보기

```python
# Class 정의 → 설계도를 만드는 것
class User:
    ...   # 일단 내용은 비워둠 (... 은 "내용 없음"을 의미)

# Instance 생성 → 설계도로 실제 객체를 찍어내는 것
user = User()       # User 설계도로 찍어낸 객체 1번
user_one = User()   # User 설계도로 찍어낸 객체 2번
user_two = User()   # User 설계도로 찍어낸 객체 3번
```

---

### Class vs Instance 차이

| | Class | Instance |
|---|---|---|
| **비유** | 붕어빵 틀 (설계도) | 실제 붕어빵 (실체) |
| **역할** | 어떤 데이터/기능을 가질지 정의 | 실제로 사용되는 객체 |
| **생성** | `class User:` 로 정의 | `user = User()` 로 생성 |
| **개수** | 보통 하나 | 여러 개 만들 수 있음 |

---

### 왜 Class가 필요할까?

지금까지 사용자 데이터를 이렇게 썼어요:

```python
# 딕셔너리로 사용자 표현 (현재 방식)
users = [
    {"id": 1, "name": "alex"},
    {"id": 2, "name": "bob"}
]
```

Class를 쓰면 이렇게 바꿀 수 있어요:

```python
# Class로 사용자 표현 (더 체계적인 방식)
class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

user1 = User(id=1, name="alex")  # Instance 생성
user2 = User(id=2, name="bob")   # Instance 생성

print(user1.name)  # "alex"
print(user2.id)    # 2
```

> 💡 **Class의 장점**
> - 데이터 구조가 명확해집니다
> - 타입 검사가 가능해집니다
> - FastAPI에서 Pydantic 모델로 발전하는 기반이 됩니다 (다음 수업에서 배울 내용!)

---

### 용어 정리

| 용어 | 설명 | 예시 |
|---|---|---|
| **Class (클래스)** | 객체를 만들기 위한 설계도/틀 | `class User:` |
| **Instance (인스턴스)** | Class로 만들어진 실체화된 객체 | `user = User()` |
| **객체 (Object)** | Instance와 같은 말 | `user`, `user_one` |
| **실체화** | Class(설계도)로 Instance(실제 객체)를 만드는 것 | `User()` 호출 |
| **`...`** | 파이썬에서 "내용 없음"을 의미하는 표현 | `class User: ...` |

---

## 10. 오늘 배운 전체 내용 요약

```python
from fastapi import FastAPI, Path, Query

app = FastAPI()

users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"},
]

# Path Parameter + 유효성 검사
@app.get("/users/{user_id}")
def get_user_handler(
    user_id: int = Path(..., ge=1),
    field: str = Query(None)
):
    user = users[user_id - 1]
    if field in ("id", "name"):
        return (field, user[field])
    return user

# Query Parameter + 유효성 검사
@app.get("/users/search")
def search_user_handler(
    name: str = Query(..., min_length=2),
    age: int = Query(None, ge=1),
):
    return {"name": name, "age": age}

# POST 요청
@app.post("/users/sign-up")
def sign_up_user_handler(name: str):
    return {"msg": f"hello {name}"}
```

---

## 11. 전체 용어 정리

| 용어 | 설명 |
|---|---|
| **Path Parameter** | URL 경로 안의 동적 변수 `/users/{user_id}` |
| **Query Parameter** | URL 뒤 `?key=value` 형태의 변수 |
| **유효성 검사** | 들어온 값이 조건에 맞는지 자동으로 확인 |
| **ge / gt / le / lt** | 숫자 범위 조건 (이상/초과/이하/미만) |
| **필수값 `...`** | 반드시 입력해야 하는 값 |
| **선택값 `None`** | 없어도 되는 값 |
| **Type Hint** | 변수/함수에 타입을 명시하는 파이썬 문법 |
| **`\|`** | 여러 타입 허용 ("또는") |
| **`->`** | 함수 반환값 타입 명시 |
| **Class** | 객체를 만들기 위한 설계도 |
| **Instance** | Class로 만들어진 실체화된 객체 |
| **422 에러** | 유효성 검사 실패 시 FastAPI가 반환하는 에러 |
| **snake_case** | 단어 사이를 `_`로 구분하는 방식 |

---

> 📌 **오늘 수업 핵심 한 줄 요약**
> `Path()`와 `Query()`로 데이터를 검증하고, Type Hint로 타입을 명시하며,
> Class(설계도)로 Instance(실제 객체)를 찍어내는 구조가 FastAPI의 기반이 된다!