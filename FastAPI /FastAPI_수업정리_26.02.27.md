# 🚀 FastAPI 수업 정리 5일차

> 작성일: 2026년 2월 27일
> 학습 내용: 동기 vs 비동기 / async / await / gather / BackgroundTasks / lifespan

---

## 📚 오늘 배운 것 한눈에 보기

| 상황 | 권장 방식 |
|---|---|
| DB 조회/저장 | 비동기 ✅ |
| 외부 API 호출 | 비동기 ✅ |
| 파일 읽기/쓰기 | 비동기 ✅ |
| 단순 계산 | 동기도 무방 |
| 대기 없는 빠른 작업 | 동기도 무방 |

---


## 1. 동기 프로그래밍 (sync.py)

### 동기란?

> **호출한 함수가 끝날 때까지 기다렸다가 다음 코드를 실행하는 방식**

```python
import time

def hello():
    time.sleep(5)   # 5초 대기
    print("hello")

hello()  # hello()가 끝날 때까지 5초 동안 아무것도 못 함
```

### 비유로 이해하기

```
동기 방식 = 배달 주문 후 문 앞에서 계속 기다리는 것

배달 요청 → (5분 대기 동안 아무것도 못 함) → 음식 받음
```

### 동기 방식의 문제

```
FastAPI 서버 ←→ DB 조회 (대기 발생!)

DB 조회하는 동안 서버는 아무것도 못 함
→ 다른 사용자의 요청도 처리 못 함
→ 비효율적!
```

> 💡 **대기가 발생하는 작업 = I/O 작업**
> - DB에서 데이터 가져오기
> - 파일 읽기/쓰기
> - 네트워크 요청 (API 호출 등)
> 이런 작업들은 대기 시간이 발생해서 비동기로 최적화할 수 있음

---

## 2. 비동기 프로그래밍 (async.py)

### 비동기란?

> **대기 시간 동안 다른 작업을 처리할 수 있는 프로그래밍 방식**

```
동기 방식  = 물 끓이는 동안 그 자리에서 계속 기다리는 것 ❌
비동기 방식 = 물 끓이는 동안 반찬도 준비하고, 카톡도 보내는 것 ✅
```

---

### async def - 비동기 함수 정의

```python
import asyncio

# 비동기 함수 (= 코루틴 함수)
async def hello():
    print("hello")
```

> 💡 **중요! async def 함수를 호출하면?**
> 즉시 실행되지 않고 **코루틴(coroutine)** 을 생성함

```python
coroutine = hello()   # 실행 ❌ → 코루틴 생성만 됨
print(coroutine)      # <coroutine object hello at 0x...>

asyncio.run(coroutine)  # ✅ 이렇게 해야 실제로 실행됨
```

---

### 코루틴(Coroutine)이란?

> **Co(같이) + Routine(함수) = 여러 개가 같이 동작하는 함수**
> 혼자 독점하지 않고, 서로 양보하면서 실행되는 함수

```
일반 함수: 혼자 끝날 때까지 독점 실행
코루틴:    여럿이 서로 양보하면서 동시에 실행
```

---

### 정리

```
1. async def로 정의하면 → 코루틴 함수가 됨
2. 코루틴 함수를 호출() → 즉시 실행 ❌, 코루틴 생성만 됨
3. 코루틴은 동시에 같이 실행되기 위한 함수들
```

---

## 3. await 키워드 (await.py)

### await란?

> **I/O 대기가 발생하는 순간, 실행권을 다른 코루틴에게 양보하는 키워드**

---

### 동기 vs 비동기 실행 시간 비교

```python
import asyncio
import time

# ===== 동기 방식 =====
def task_a():
    print("A 시작")
    time.sleep(3)    # 3초 대기 (양보 없음)
    print("A 끝")

def task_b():
    print("B 시작")
    time.sleep(3)    # 3초 대기 (양보 없음)
    print("B 끝")

task_a()  # A가 끝날 때까지 3초 대기
task_b()  # B가 끝날 때까지 3초 대기
# 총 소요시간: 6초 ❌


# ===== 비동기 방식 =====
async def coro_a():
    print("A 시작")          # 1번째
    await asyncio.sleep(3)   # 2번째 → 양보! B에게 실행권 넘김
    print("A 끝")            # 5번째

async def coro_b():
    print("B 시작")          # 3번째
    await asyncio.sleep(3)   # 4번째 → 양보! A에게 실행권 넘김
    print("B 끝")            # 6번째

async def main():
    await asyncio.gather(coro_a(), coro_b())  # 동시 실행!

asyncio.run(main())
# 총 소요시간: 3초 ✅ (2배 빠름!)
```

### 실행 순서 시각화

```
시간 →  0초            3초
        │             │
coro_a: [A 시작][대기...][A 끝]
coro_b:      [B 시작][대기...][B 끝]
             ↑
         A가 양보하는 순간 B 시작
```

---

### await를 쓰는 두 가지 조건 🌟

```python
# 조건 1: 반드시 async def 함수 안에서만 사용 가능
async def my_func():
    await some_task()   # ✅

def my_func():
    await some_task()   # ❌ SyntaxError!


# 조건 2: awaitable한 작업에만 사용
# awaitable 판단 기준:
#   - async def로 정의된 함수인가?
#   - 비동기 라이브러리에서 온 함수인가?
#   - I/O 대기 시간이 발생하는 작업인가?

await asyncio.sleep(3)       # ✅ 비동기 라이브러리
await session.execute(stmt)  # ✅ DB I/O 작업
await time.sleep(3)          # ❌ time.sleep은 awaitable이 아님!
```

---

### 비동기 방식의 단점

```
1. 코루틴이 정확히 어떤 순서로 실행될지 보장할 수 없음
2. 잘못 사용하면 오히려 더 비효율적으로 동작할 수 있음
→ 비동기 프로그래밍의 실행 흐름을 이해하고 사용해야 함!
```

---

## 4. gather() (gather.py)

### gather()란?

> **여러 코루틴을 동시에 실행시키는 함수**
> gather = "모으다"

```python
import asyncio

async def hello():
    print("hello")

coro1 = hello()
coro2 = hello()

async def main():
    await asyncio.gather(coro1, coro2)  # coro1, coro2 동시 실행!

asyncio.run(main())
```

---

### ⚠️ 비동기 문법 써도 동기로 동작할 수 있음!

```python
# ❌ 이렇게 하면 동기 방식과 똑같음!
asyncio.run(coro1)   # coro1 끝날 때까지 기다림
asyncio.run(coro2)   # 그 다음 coro2 실행

# ✅ gather로 묶어야 진짜 동시 실행!
async def main():
    await asyncio.gather(coro1, coro2)
```

> 💡 **핵심 포인트**
> 비동기 문법(`async`, `await`)을 썼다고 자동으로 비동기로 동작하지 않음
> **`gather()`로 묶어야** 진짜 동시에 실행됨

### 정리

```
1. 코루틴은 동시에 실행되기 위한 함수들
2. 코루틴을 하나만 실행할 거면 굳이 비동기로 할 이유 없음
3. 비동기 문법을 써도 실제로는 동기처럼 동작할 수 있음 (조심!)
4. 코루틴을 동시에 실행하려면 gather() 사용!
```

---

## 5. blocking (blocking.py) ⚠️

### blocking이란?

> **비동기 환경에서 실행권을 양보하지 않고 혼자 독점하는 나쁜 코드**

```python
import asyncio
import time

async def good_task():
    print("착한 Task 시작")
    await asyncio.sleep(5)  # ✅ 양보! 다른 코루틴 실행 가능
    print("착한 Task 종료")

async def bad_task():
    print("나쁜 Task 시작")
    time.sleep(5)           # ❌ 양보 없음! 전체가 멈춤 (blocking!)
    print("나쁜 Task 종료")

async def main():
    await asyncio.gather(
        good_task(),
        good_task(),
        good_task(),
        bad_task(),    # ← 이 녀석 때문에 전체가 막힘!
    )
```

### 실행 결과 비교

```
good_task만 있을 때:
착한1 시작 → 착한2 시작 → 착한3 시작 → (모두 동시 대기) → 착한1,2,3 종료
총 소요시간: 5초 ✅

bad_task 포함될 때:
착한1 시작 → 착한2 시작 → 착한3 시작 → 나쁜 시작
→ time.sleep(5) 동안 전체가 멈춤! ← 여기서 문제!
→ 나쁜 종료 → 그제서야 착한1,2,3 종료
총 소요시간: 10초 ❌
```

### blocking이 발생하는 코드들

| 나쁜 코드 ❌ | 좋은 코드 ✅ |
|---|---|
| `time.sleep(5)` | `await asyncio.sleep(5)` |
| `requests.get(url)` | `await httpx.get(url)` |
| 동기 DB 드라이버 | 비동기 DB 드라이버 |

> 💡 **FastAPI에서 blocking이 문제인 이유**
> FastAPI는 기본적으로 비동기로 동작
> `time.sleep()` 같은 blocking 코드가 있으면
> 그 시간 동안 **다른 모든 사용자의 요청이 멈춰버림!**

---

## 6. main.py에 추가된 내용

### BackgroundTasks (백그라운드 작업) ⭐

#### BackgroundTasks란?

> **응답을 먼저 클라이언트에게 보내고, 시간이 오래 걸리는 작업을 백그라운드에서 실행하는 기능**

---

#### 문제 상황 (BackgroundTasks 없이)

```python
def send_email(name: str):
    import time
    time.sleep(5)   # 이메일 전송에 5초 걸림
    print(f"{name}에게 이메일 전송 완료")

@app.post("/users/sign-up")
def sign_up_handler(body: UserSignUpRequest):
    # 1) DB에 저장
    session.add(new_user)
    session.commit()

    # 2) 이메일 전송 (5초 대기!)
    send_email(name=body.name)  # ← 사용자는 5초를 기다려야 함 ❌

    return new_user
```

```
클라이언트: 회원가입 요청
서버:       DB 저장 → 이메일 전송(5초 대기) → 응답
클라이언트: 5초 후에야 응답 받음 😤
```

---

#### 해결 (BackgroundTasks 사용)

```python
from fastapi import BackgroundTasks

def send_email(name: str):
    import time
    time.sleep(5)
    print(f"{name}에게 이메일 전송 완료")

@app.post("/users/sign-up")
def sign_up_handler(
    body: UserSignUpRequest,
    background_tasks: BackgroundTasks,  # FastAPI가 자동 주입
    session = Depends(get_session),
):
    # 1) DB에 저장
    new_user = User(name=body.name, age=body.age)
    session.add(new_user)
    session.commit()

    # 2) 이메일 전송을 백그라운드에 등록
    background_tasks.add_task(send_email, body.name)
    #                ^^^^^^^^  ^^^^^^^^^  ^^^^^^^^^
    #                등록 함수   실행할 함수  함수의 인자

    return new_user  # ← 이메일 전송 기다리지 않고 바로 응답! ✅
```

```
클라이언트: 회원가입 요청
서버:       DB 저장 → 응답 바로 반환 ✅
            (백그라운드에서 이메일 전송 진행 중...)
클라이언트: 즉시 응답 받음 😊
```

---

#### addEventListener와 비슷한 개념

```javascript
// JS의 이벤트 리스너
addEventListener("click", handleClick)
//                         ↑ 함수 자체를 등록

// FastAPI의 BackgroundTasks
background_tasks.add_task(send_email, body.name)
//                         ↑ 함수 자체를 등록
```

같은 패턴이에요! 함수를 **바로 실행하는 게 아니라 등록**하는 것!

---

### lifespan - 서버 시작/종료 시 실행할 코드

```python
import anyio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(_):
    # ===== 서버 시작할 때 실행 =====
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 200  # 스레드 풀 개수를 200개로 늘림
    yield  # ← 여기서 서버 실행 (요청 받기 시작)
    # ===== 서버 종료할 때 실행 =====
    # (여기에 정리 코드 작성)

app = FastAPI(lifespan=lifespan)
```

#### lifespan 흐름

```
서버 시작
    │
    ├─ yield 위: 스레드 풀 설정 등 초기화 작업
    │
    yield ← 서버 가동! 요청 받기 시작
    │
    ├─ yield 아래: 서버 종료 시 정리 작업
    │
서버 종료
```

#### 스레드 풀(Thread Pool)이란?

```python
limiter.total_tokens = 200  # 스레드 풀 개수 200개
```

> FastAPI에서 동기 함수(`def`)는 스레드 풀에서 실행됨
> 기본값은 40개인데, 동시 요청이 많을 때 200개로 늘려서
> 더 많은 요청을 동시에 처리할 수 있게 함

---

## 7. 동기 vs 비동기 최종 정리

### 실행 시간 비교

```
3초씩 걸리는 작업 3개를 실행할 때:

동기 방식:   [작업1: 3초][작업2: 3초][작업3: 3초] = 총 9초 ❌
비동기 방식: [작업1: 3초]
             [작업2: 3초]  ← 동시 실행!
             [작업3: 3초]
             = 총 3초 ✅ (3배 빠름!)
```

### 언제 비동기를 써야 할까?

| 상황 | 권장 방식 |
|---|---|
| DB 조회/저장 | 비동기 ✅ |
| 외부 API 호출 | 비동기 ✅ |
| 파일 읽기/쓰기 | 비동기 ✅ |
| 단순 계산 | 동기도 무방 |
| 대기 없는 빠른 작업 | 동기도 무방 |

---


## 8. 전체 개념 연결 흐름

```
클라이언트  →  POST /users/sign-up 요청
                │
                ├─ BackgroundTasks 주입 (FastAPI 자동)
                ├─ session 주입 (Depends(get_session))
                │
                ├─ DB 저장 (session.add + commit)
                ├─ 이메일 전송 백그라운드 등록 (add_task)
                │
                → 응답 즉시 반환 ✅
                │
                (백그라운드에서 send_email 실행 중...)
```

---

## 9. 용어 정리
| 용어 | 설명 |
|---|---|
| **동기 (Sync)** | 한 작업이 끝날 때까지 기다렸다가 다음 작업 실행 |
| **비동기 (Async)** | 대기 시간 동안 다른 작업을 처리할 수 있는 방식 |
| **I/O 작업** | DB, 파일, 네트워크 등 입출력 작업 (대기 발생) |
| **async def** | 비동기 함수(코루틴 함수)를 정의하는 키워드 |
| **코루틴** | 서로 양보하면서 동시에 실행되는 함수 |
| **await** | I/O 대기 순간 실행권을 양보하는 키워드 |
| **asyncio** | 파이썬 비동기 표준 라이브러리 |
| **asyncio.run()** | 코루틴을 실제로 실행하는 함수 |
| **asyncio.gather()** | 여러 코루틴을 동시에 실행하는 함수 |
| **blocking** | 비동기 환경에서 실행권을 양보하지 않는 코드 |
| **BackgroundTasks** | 응답 후 백그라운드에서 작업을 실행하는 FastAPI 기능 |
| **add_task()** | BackgroundTasks에 실행할 함수를 등록하는 메서드 |
| **lifespan** | 서버 시작/종료 시 실행할 코드를 등록하는 기능 |
| **스레드 풀** | 동기 함수를 실행하기 위해 미리 만들어둔 스레드 묶음 |
| **asynccontextmanager** | async with 문을 지원하는 데코레이터 |

---

> 📌 **오늘 수업 핵심 한 줄 요약**
> 비동기는 대기 시간 동안 다른 작업을 처리해 효율을 높이는 방식이며,
> `async/await`로 코루틴을 만들고 `gather()`로 동시 실행,
> `BackgroundTasks`로 무거운 작업을 응답 후 처리한다!
