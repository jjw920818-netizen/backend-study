# 🚀 FastAPI 수업 정리 4일차

> 작성일: 2026년 2월 28일
> 학습 내용: SQLAlchemy / DB 연동 / ORM / Session / DELETE API

---

## 📚 오늘 배운 것 한눈에 보기

| 주제 | 이전 수업 | 오늘 새로 배운 것 |
|---|---|---|
| 데이터 저장 | 리스트 `users = [...]` (임시) | ✅ 실제 DB (SQLite) |
| 데이터 조회 | `users[user_id - 1]` | ✅ `select(User).where(...)` |
| 데이터 생성 | `users.append(new_user)` | ✅ `session.add()` + `session.commit()` |
| 데이터 수정 | `user["name"] = body.name` | ✅ `user.name = body.name` + `session.commit()` |
| 데이터 삭제 | ❌ 없었음 | ✅ `session.delete()` + `session.commit()` |
| 파일 구조 | `main.py`, `schema.py` | ✅ `models.py`, `db_connection.py` 추가 |
| 터미널 실습 | - | ✅ mappings vs scalars 직접 비교 |
| 의존성 주입 | - | ✅ `Depends(get_session)` |

---

## 1. 새로운 파일 구조

```
📁 프로젝트 폴더
├── main.py           ← API 엔드포인트 정의
├── schema.py         ← 요청/응답 데이터 형태 정의 (Pydantic)
├── models.py         ← DB 테이블 구조 정의 (SQLAlchemy) ✅ 신규
├── db_connection.py  ← DB 연결 설정 ✅ 신규
└── test.db           ← 실제 DB 파일 (자동 생성) ✅ 신규
```

---

## 2. ORM이란? (핵심 개념!) ⭐

### 기존 방식 vs ORM 방식

지금까지 데이터를 이렇게 다뤘어요:

```python
# 기존 방식 - 파이썬 리스트로 임시 저장
users = [
    {"id": 1, "name": "alex", "age": 20},
]
users.append({"id": 4, "name": "new"})  # 추가
```

서버를 껐다 켜면 데이터가 **전부 사라집니다!** ❌

---

ORM을 쓰면 파이썬 코드로 DB를 다룰 수 있어요:

```python
# ORM 방식 - 파이썬 클래스로 DB 테이블을 다룸
new_user = User(name="alex", age=20)  # 파이썬 객체 생성
session.add(new_user)                 # DB에 추가
session.commit()                      # DB에 저장 확정
```

서버를 꺼도 **데이터가 DB 파일에 남아있습니다!** ✅

---

### ORM 정의

> **ORM (Object-Relational Mapping)**
> 파이썬 클래스(객체)와 DB 테이블을 연결해주는 기술
> 복잡한 SQL 쿼리 대신 파이썬 코드로 DB를 다룰 수 있게 해줌

| SQL 방식 | ORM 방식 (SQLAlchemy) |
|---|---|
| `SELECT * FROM user` | `select(User)` |
| `SELECT * FROM user WHERE id=1` | `select(User).where(User.id == 1)` |
| `INSERT INTO user ...` | `session.add(new_user)` |
| `DELETE FROM user WHERE id=1` | `session.delete(user)` |

---

## 3. models.py - DB 테이블 정의

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(32))
    age: Mapped[int] = mapped_column(Integer, nullable=True)
```

### import 하나씩 설명

```python
from sqlalchemy import Integer, String
```

| import | 설명 |
|---|---|
| `Integer` | DB에서 정수형 컬럼 타입 |
| `String` | DB에서 문자열 컬럼 타입 |

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
```

| import | 설명 |
|---|---|
| `DeclarativeBase` | 모든 DB 모델의 부모 클래스, 이걸 상속받아야 DB 테이블로 인식 |
| `Mapped` | 컬럼의 파이썬 타입을 명시하는 Type Hint용 문법 |
| `mapped_column` | 컬럼의 DB 설정(타입, 제약조건 등)을 지정하는 함수 |

---

### 코드 한 줄씩 설명

```python
class Base(DeclarativeBase):
    pass
```
> SQLAlchemy가 권장하는 방식으로 커스텀 기본 클래스를 만드는 것
> 모든 DB 모델은 이 `Base`를 상속받아야 해요

---

```python
class User(Base):           # Base를 상속 → DB 테이블로 인식
    __tablename__ = "user"  # 실제 DB에 생성될 테이블 이름
```

---

```python
id: Mapped[int] = mapped_column(Integer, primary_key=True)
#   ^^^^^^^^^       ^^^^^^^^^^^  ^^^^^^^  ^^^^^^^^^^^^^^^^
#   파이썬 타입힌트   DB 컬럼 설정  정수형   기본키(고유 식별자)
```

```python
name: Mapped[str] = mapped_column(String(32))
#                                 ^^^^^^^^^
#                                 최대 32글자 문자열
```

```python
age: Mapped[int] = mapped_column(Integer, nullable=True)
#                                          ^^^^^^^^^^^^^
#                                          null 허용 (없어도 됨)
```

---

### schema.py의 UserResponse vs models.py의 User 차이

| | `UserResponse` (schema.py) | `User` (models.py) |
|---|---|---|
| **역할** | API 응답 형태 정의 | DB 테이블 구조 정의 |
| **부모 클래스** | `BaseModel` (Pydantic) | `Base` (SQLAlchemy) |
| **사용 위치** | 클라이언트 ↔ 서버 사이 | 서버 ↔ DB 사이 |

---

## 4. db_connection.py - DB 연결 설정

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)

SessionFactory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

def get_session():
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
```

### import 하나씩 설명

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
```

| import | 설명 |
|---|---|
| `create_engine` | DB와의 연결을 만들어주는 함수 |
| `sessionmaker` | Session 클래스를 만들어주는 함수 |

---

### DATABASE_URL 구조

```python
DATABASE_URL = "sqlite:///./test.db"
#               ^^^^^^  ^^ ^^^^^^^
#               DB종류  //  파일경로
```

| 부분 | 의미 |
|---|---|
| `sqlite://` | SQLite DB를 사용하겠다 |
| `/./test.db` | 현재 프로젝트 폴더에 `test.db` 파일로 저장 |

> 💡 **SQLite란?**
> 파일 하나로 동작하는 가벼운 DB예요.
> 서버 없이 파일만으로 DB 기능을 사용할 수 있어서 학습용으로 많이 씁니다!

---

### Engine vs Session 차이

```
engine      → DB와의 연결 자체 (도로)
session     → 실제 데이터를 주고받는 작업 단위 (자동차)
```

| | Engine | Session |
|---|---|---|
| **비유** | DB로 가는 도로 | 도로 위를 달리는 자동차 |
| **역할** | DB 연결 유지 | 실제 데이터 CRUD 작업 |
| **생성** | `create_engine()` | `SessionFactory()` |

---

### SessionFactory 옵션 설명

```python
SessionFactory = sessionmaker(
    bind=engine,          # 어떤 DB에 연결할지
    autocommit=False,     # 자동 저장 끄기 (수동으로 commit() 해야 함)
    autoflush=False,      # 자동 flush 끄기
    expire_on_commit=False, # commit 후 데이터 만료 안 시킴
)
```

> 💡 **commit이란?**
> DB에 변경사항을 최종 확정하는 것입니다.
> commit 전까지는 DB에 실제로 반영되지 않아요!

---

### return vs yield

```python
# return → 값을 반환하고 함수 완전히 종료
def get_data():
    return "data"  # 끝!

# yield → 값을 반환하고 함수를 일시정지 (나중에 재개 가능)
def get_session():
    session = SessionFactory()
    try:
        yield session      # 여기서 일시정지, session을 밖에서 사용
    finally:
        session.close()    # 사용 끝나면 여기서 재개 → 세션 닫기
```

> 💡 **yield를 쓰는 이유**
> session을 다 쓰고 나서 **반드시 close()가 실행되도록** 보장하기 위해서예요.
> try/finally와 함께 쓰면 에러가 나도 항상 close()가 실행됩니다!

---

### with 문 (컨텍스트 매니저)

```python
# with 문 없이
session = SessionFactory()
session.add(new_user)
session.commit()
session.close()  # 직접 닫아야 함 (까먹으면 문제!)

# with 문 사용
with SessionFactory() as session:
    session.add(new_user)
    session.commit()
# with 블록 벗어나면 자동으로 close() 호출 ✅
```

> 💡 **with 문을 쓰는 이유**
> `close()`를 깜빡해도 자동으로 세션이 닫혀요!

---

## 5. main.py - DB 연동된 API

### 새로운 import 설명

```python
from fastapi import FastAPI, Path, Query, Body, status, HTTPException, Depends
from sqlalchemy import select
from db_connection import SessionFactory, get_session
from models import User
from schema import UserSignUpRequest, UserResponse, UserUpdateRequest
```

| import | 설명 |
|---|---|
| `Depends` | FastAPI의 의존성 주입 도구 |
| `select` | SQLAlchemy에서 SELECT 쿼리를 만드는 함수 |
| `SessionFactory` | 세션을 생성하는 클래스 |
| `get_session` | 세션을 제공하는 함수 |
| `User` | DB 테이블과 연결된 모델 클래스 |

---

### 전체 사용자 조회 API

```python
@app.get("/users",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse],  # 리스트 형태로 응답
)
def get_users_handler(session=Depends(get_session)):
    with SessionFactory() as session:
        stmt = select(User)              # SELECT * FROM user
        result = session.execute(stmt)   # 쿼리 실행
        users = result.scalars().all()   # 결과를 리스트로 변환
    return users
```

#### `select(User)` 부터 `scalars().all()` 까지 흐름

```
select(User)
    → "SELECT * FROM user" 라는 쿼리 구문 생성 (아직 실행 안 함)

session.execute(stmt)
    → 쿼리를 실제로 DB에 보내서 실행
    → 결과(result) 반환

result.scalars()
    → 결과에서 User 객체들만 추출
    → [<User id=1>, <User id=2>, ...] 형태

.all()
    → 전체를 파이썬 리스트로 변환
    → [User1, User2, User3]
```

| 메서드 | 역할 |
|---|---|
| `select(User)` | SELECT 쿼리 구문 생성 |
| `session.execute(stmt)` | 쿼리 실행 |
| `result.scalars()` | 결과에서 객체만 추출 |
| `.all()` | 전체 결과를 리스트로 반환 |
| `result.scalar()` | 결과 1개만 반환 (단일 조회 시) |

---

### 단일 사용자 조회 API

```python
@app.get("/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
def get_user_handler(
    user_id: int = Path(..., ge=1, description="사용자의 ID"),
):
    with SessionFactory() as session:
        stmt = select(User).where(User.id == user_id)  # WHERE id = user_id
        result = session.execute(stmt)
        user = result.scalar()   # 1개만 가져오기

    if user is None:             # 없으면 404 에러
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 사용자 ID입니다",
        )
    return user
```

#### `.where()` 사용법

```python
select(User).where(User.id == user_id)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#            WHERE id = 1 과 같은 의미
```

> 💡 **이전 수업 방식 vs 오늘 방식**
>
> ```python
> # 이전: 리스트에서 인덱스로 찾기
> user = users[user_id - 1]
>
> # 오늘: DB에서 조건으로 찾기
> stmt = select(User).where(User.id == user_id)
> user = result.scalar()
> ```

---

### 회원가입 API

```python
@app.post("/users/sign-up",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
def sign_up_handler(body: UserSignUpRequest):
    new_user = User(name=body.name, age=body.age)  # User 객체 생성

    with SessionFactory() as session:
        session.add(new_user)    # DB에 추가 준비
        session.commit()         # DB에 최종 저장

    return new_user
```

#### DB 저장 흐름

```
User(name="Alice", age=20)
    → 파이썬 객체 생성 (아직 DB에 없음)

session.add(new_user)
    → DB에 추가할 준비 (아직 저장 안 됨)

session.commit()
    → DB에 실제로 저장 확정! ✅
```

---

### 사용자 수정 API (PATCH)

```python
@app.patch("/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
def update_user_handler(
    user_id: int = Path(..., ge=1),
    body: UserUpdateRequest = Body(...),
):
    # 1) 수정할 데이터 검증
    if body.name is None and body.age is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 데이터가 없습니다",
        )

    with SessionFactory() as session:
        # 2) 사용자 조회
        stmt = select(User).where(User.id == user_id)
        user = session.execute(stmt).scalar()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 사용자 ID입니다.",
            )

        # 3) 수정
        if body.name is not None:
            user.name = body.name   # 딕셔너리 → 객체 속성으로 변경!

        if body.age is not None:
            user.age = body.age

        session.commit()  # ⭐ 꼭 해줘야 DB에 반영됨!

    return user
```

> 💡 **이전 수업 방식 vs 오늘 방식**
>
> ```python
> # 이전: 딕셔너리 방식
> user["name"] = body.name
>
> # 오늘: 객체 속성 방식
> user.name = body.name
> # User가 딕셔너리가 아닌 클래스 객체이기 때문!
> ```

---

### 사용자 삭제 API (DELETE) ✅ 오늘 처음 배운 것!

```python
@app.delete("/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,  # 응답 본문 없음
)
def delete_user_handler(user_id: int = Path(..., ge=1)):
    with SessionFactory() as session:
        stmt = select(User).where(User.id == user_id)
        user = session.execute(stmt).scalar()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 사용자 ID입니다.",
            )

        session.delete(user)   # 삭제 준비
        session.commit()       # DB에 삭제 확정

    return  # 204는 응답 본문이 없음!
```

#### 204 No Content

```python
status_code=status.HTTP_204_NO_CONTENT
```

> 삭제 성공 시 돌려줄 데이터가 없기 때문에 **204** 를 씁니다.
> `return` 뒤에 아무것도 없는 것도 같은 이유예요!

---

## 6. CRUD 전체 정리

> **CRUD** = Create(생성) / Read(조회) / Update(수정) / Delete(삭제)
> 모든 데이터 관련 앱의 기본 4가지 기능이에요!

| CRUD | HTTP Method | URL | 핵심 코드 |
|---|---|---|---|
| **Create** | POST | `/users/sign-up` | `session.add()` + `session.commit()` |
| **Read (전체)** | GET | `/users` | `select(User)` + `.scalars().all()` |
| **Read (단일)** | GET | `/users/{user_id}` | `select(User).where(...)` + `.scalar()` |
| **Update** | PATCH | `/users/{user_id}` | `user.name = ...` + `session.commit()` |
| **Delete** | DELETE | `/users/{user_id}` | `session.delete(user)` + `session.commit()` |

---

## 7. session 작업 순서 정리

```
모든 DB 작업은 이 순서를 따릅니다!

with SessionFactory() as session:
    │
    ├─ 1) 조회: select(User).where(...)
    │         session.execute(stmt).scalar()
    │
    ├─ 2) 작업: session.add()    ← 추가
    │          user.name = ...  ← 수정
    │          session.delete() ← 삭제
    │
    └─ 3) 확정: session.commit() ⭐ 꼭 필요!

# with 블록 종료 → session.close() 자동 호출
```

---

## 8. 전체 파일 역할 요약

```
클라이언트 (브라우저/앱)
    │  요청/응답
    ▼
main.py (API 엔드포인트)
    │  데이터 형태 검증
    ├── schema.py (Pydantic 모델)
    │  DB 작업
    ├── db_connection.py (세션 관리)
    │  테이블 구조
    └── models.py (SQLAlchemy 모델)
            │
            ▼
        test.db (실제 DB 파일)
```

---

## 9. 터미널 직접 실습 - DB 조작 해보기 ⭐

오늘 터미널에서 파이썬 인터프리터로 직접 DB를 조작해봤어요!

### 실습 흐름 전체

```python
>>> from db_connection import SessionFactory
>>> from sqlalchemy import select
>>> from models import User

>>> session = SessionFactory()   # 세션 생성
>>> stmt = select(User)          # 쿼리 구문 생성 (아직 실행 안 함)

>>> print(stmt)
SELECT "user".id, "user".name, "user".age FROM "user"
# → 파이썬 코드가 실제 SQL로 변환된 모습!
```

---

### mappings() vs scalars() 차이

같은 쿼리 결과를 꺼내는 두 가지 방법이에요.

```python
# 방법 1: mappings().all()
>>> result = session.execute(stmt)
>>> result.mappings().all()
[{'User': <models.User object at 0x...>}, {'User': <models.User object at 0x...>}]
# → {'User': 객체} 딕셔너리 형태로 감싸져 있음
# → mappings[0]["User"].id 처럼 꺼내야 함

# 방법 2: scalars().all() ✅ 실제로 쓰는 방법
>>> result = session.execute(stmt)
>>> result.scalars().all()
[<models.User object at 0x...>, <models.User object at 0x...>]
# → User 객체 리스트로 바로 반환
# → scalars[0].id 처럼 바로 꺼낼 수 있음
```

| | `mappings().all()` | `scalars().all()` |
|---|---|---|
| **결과 형태** | `[{'User': 객체}, ...]` | `[객체, 객체, ...]` |
| **값 접근** | `mappings[0]["User"].id` | `scalars[0].id` |
| **실제 사용** | 거의 안 씀 | ✅ 주로 이걸 씀 |

---

### .where() 로 단일 조회

```python
>>> stmt = select(User).where(User.id == 1)
>>> user = session.execute(stmt).scalar()   # 1개만 꺼내기

>>> user.id    # 1
>>> user.name  # 'alice'
>>> user.age   # 20
```

---

### 오늘 만난 에러들

```python
# 에러 1: 오타 (excute → execute)
>>> session.excute(stmt)
AttributeError: 'Session' object has no attribute 'excute'.
# Did you mean: 'execute'?  ← 파이썬이 친절하게 알려줌!

# 에러 2: str에 .age 접근 시도
>>> mappings[0]["User"].name.age
AttributeError: 'str' object has no attribute 'age'
# name은 문자열(str)이라 .age가 없음! .age는 User 객체에 있어야 함
# 올바른 방법:
>>> mappings[0]["User"].age   # ✅
```

---

### DB 데이터 직접 수정해보기

```python
>>> user.age = 30      # 파이썬 객체 값 변경
>>> user.age           # 30 (메모리에서는 바뀜)
>>> session.commit()   # ⭐ DB에 실제 반영!
```

> 💡 `session.commit()` 없이 `user.age = 30`만 하면
> 메모리에서만 바뀌고 DB에는 반영이 안 돼요!

---

## 10. 의존성 주입 (Dependency Injection) ⭐

### 의존성 주입이란?

> **"필요한 것을 직접 만들지 말고, 외부에서 받아서 써라"**

쉽게 말하면, 함수가 필요한 것(세션 등)을 **FastAPI가 자동으로 만들어서 넣어주는 것**이에요.

---

### Depends 없이 vs Depends 사용

```python
# ❌ Depends 없이 - 매번 직접 세션 만들기
def get_users_handler():
    with SessionFactory() as session:   # 함수 안에서 직접 만듦
        ...

# ✅ Depends 사용 - FastAPI가 세션을 만들어서 넣어줌
def get_users_handler(
    session = Depends(get_session)   # FastAPI가 get_session() 실행해서 session 주입
):
    stmt = select(User)
    users = session.execute(stmt).scalars().all()
    return users
```

---

### 동작 흐름

```
GET /users 요청이 들어옴
    │
    ├─ FastAPI: "session 파라미터에 Depends(get_session) 있네?"
    │
    ├─ FastAPI가 get_session() 자동 실행
    │   → session = SessionFactory()
    │   → yield session  (세션을 핸들러에 전달)
    │
    ├─ get_users_handler(session=session) 실행
    │
    └─ 함수 끝나면 get_session() 재개
        → session.close() 자동 실행 ✅
```

---

### Depends의 장점

| | Depends 없이 | Depends 사용 |
|---|---|---|
| **세션 생성** | 함수마다 직접 작성 | FastAPI가 자동으로 |
| **세션 종료** | 직접 close() 해야 함 | 자동으로 close() |
| **코드 중복** | API마다 같은 코드 반복 | 한 번만 정의하면 됨 |
| **테스트** | 어려움 | 쉽게 교체 가능 |

---

### 실제 코드 비교

```python
# get_session() 함수 (db_connection.py)
def get_session():
    session = SessionFactory()
    try:
        yield session      # 여기서 세션을 핸들러에 전달
    finally:
        session.close()    # 핸들러 끝나면 자동 실행

# main.py에서 Depends로 주입
@app.get("/users")
def get_users_handler(
    session = Depends(get_session)   # get_session이 만든 session을 여기에 주입
):
    users = session.execute(select(User)).scalars().all()
    return users
```

> 💡 **핵심 포인트**
> `Depends(get_session)` 은 `get_session` **함수 자체**를 넘기는 거예요.
> `get_session()` 처럼 `()` 붙여서 실행한 결과를 넘기는 게 아니에요!

---

## 11. 용어 정리

| 용어 | 설명 |
|---|---|
| **ORM** | 파이썬 객체와 DB 테이블을 연결해주는 기술 |
| **SQLAlchemy** | 파이썬에서 가장 많이 쓰는 ORM 라이브러리 |
| **SQLite** | 파일 하나로 동작하는 가벼운 DB (학습용) |
| **Engine** | DB와의 연결을 관리하는 객체 |
| **Session** | 실제 DB 작업을 수행하는 작업 단위 |
| **commit()** | DB에 변경사항을 최종 확정하는 것 |
| **select()** | SELECT 쿼리를 만드는 함수 |
| **where()** | 조건을 추가하는 메서드 |
| **scalars().all()** | 쿼리 결과 전체를 리스트로 반환 |
| **scalar()** | 쿼리 결과 1개만 반환 |
| **yield** | 값을 반환하고 함수를 일시정지 (return과 다름) |
| **with 문** | 블록 종료 시 자동으로 close() 호출 |
| **CRUD** | Create / Read / Update / Delete |
| **204 No Content** | 성공했지만 응답 본문이 없을 때 쓰는 상태 코드 |
| **primary_key** | 각 행을 고유하게 식별하는 컬럼 (중복 불가) |
| **nullable** | null 값(빈 값)을 허용할지 여부 |
| **mappings().all()** | 쿼리 결과를 딕셔너리 형태로 반환 |
| **scalars().all()** | 쿼리 결과를 객체 리스트로 반환 (주로 사용) |
| **scalar()** | 쿼리 결과 1개를 객체로 반환 |
| **의존성 주입** | 필요한 것을 직접 만들지 않고 외부에서 받아 쓰는 방식 |
| **Depends** | FastAPI의 의존성 주입 도구, 자동으로 세션 등을 주입해줌 |

---

> 📌 **오늘 수업 핵심 한 줄 요약**
> SQLAlchemy ORM으로 DB와 연결하고, Session으로 데이터를 주고받으며,
> select / add / delete + commit() 으로 CRUD를 완성한다!
