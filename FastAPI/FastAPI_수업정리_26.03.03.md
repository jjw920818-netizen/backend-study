# 🚀 FastAPI 수업 정리 6일차

> 작성일: 2026년 3월 3일
> 학습 내용: 비동기 DB 연결 / Generator / yield / LLM / Streaming Response

---

## 📚 오늘 배운 것 한눈에 보기

| 주제 | 설명 |
|---|---|
| **비동기 DB 연결** | `db_connection_async.py` - 동기 세션을 비동기로 전환 |
| **async def 핸들러** | 모든 API 핸들러를 `async def`로 변경, `await` 추가 |
| **Generator** | `yield`로 값을 하나씩 순서대로 내보내는 함수 |
| **return vs yield** | return은 한 번에 끝, yield는 일시정지하며 여러 번 |
| **LLM 연동** | `llama-cpp-python`으로 로컬 AI 모델 실행 |
| **StreamingResponse** | AI 답변을 토큰 단위로 실시간 전송 |
| **app.state** | 서버 전체에서 공유하는 데이터를 저장하는 공간 |

---

## 1. 비동기 DB 연결 (db_connection_async.py)

### 기존 동기 방식 vs 오늘 비동기 방식

```python
# 기존 동기 방식 (db_connection.py)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine, ...)

# 오늘 비동기 방식 (db_connection_async.py)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # URL이 달라짐!
async_engine = create_async_engine(DATABASE_URL)
AsyncSessionFactory = sessionmaker(class_=AsyncSession, ...)
```

### 달라진 점 비교

| | 동기 (기존) | 비동기 (오늘) |
|---|---|---|
| **URL** | `sqlite:///./test.db` | `sqlite+aiosqlite:///./test.db` |
| **엔진** | `create_engine()` | `create_async_engine()` |
| **세션 클래스** | 기본 Session | `class_=AsyncSession` 명시 |
| **세션 종료** | `session.close()` | `await session.close()` |
| **DB 실행** | `session.execute(stmt)` | `await session.execute(stmt)` |
| **커밋** | `session.commit()` | `await session.commit()` |

---

### db_connection_async.py 전체 코드 설명

```python
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# sqlite+aiosqlite: 비동기용 SQLite 드라이버 사용
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 비동기 엔진 생성
async_engine = create_async_engine(DATABASE_URL)

# 비동기 세션 팩토리 생성
AsyncSessionFactory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,   # ← 이게 핵심! 비동기 세션 클래스 지정
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

async def get_async_session():
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()   # ← await 추가! 네트워크 작업이라 비동기 필요
```

> 💡 **왜 `await session.close()`일까?**
> 세션을 닫을 때 DB와의 네트워크 연결을 끊는 작업이 발생하기 때문에
> I/O 작업이므로 `await`가 필요!

---

## 2. main.py 변경사항 - 동기 → 비동기

### 핸들러 함수 변경

```python
# 기존 동기 방식
def get_users_handler(session = Depends(get_session)):
    with SessionFactory() as session:
        result = session.execute(stmt)      # await 없음
        ...

# 오늘 비동기 방식
async def get_users_handler(session = Depends(get_async_session)):
    result = await session.execute(stmt)    # await 추가!
    ...
```

### 바뀐 부분 요약

| 변경 전 | 변경 후 |
|---|---|
| `def` | `async def` |
| `Depends(get_session)` | `Depends(get_async_session)` |
| `session.execute(stmt)` | `await session.execute(stmt)` |
| `session.commit()` | `await session.commit()` |
| `with SessionFactory() as session:` | 제거 (Depends로 주입받아서 불필요) |

---

## 3. Generator와 yield ⭐

### Generator란?

> **값을 한 번에 다 만들어서 반환하는 게 아니라,
> 하나씩 순서대로 필요할 때마다 꺼내주는 함수**

---

### return vs yield 차이

```python
# return → 한 번에 전부 반환하고 함수 종료
def count_return():
    return [1, 2, 3]   # 리스트로 한 번에 반환

result = count_return()
print(result)   # [1, 2, 3] 한 번에 출력


# yield → 값을 하나씩 내보내고 일시정지
def count_yield():
    yield 1   # 1 반환 후 일시정지
    yield 2   # 2 반환 후 일시정지
    yield 3   # 3 반환 후 일시정지

gen = count_yield()   # 제너레이터 객체 생성 (아직 실행 안 됨!)
```

---

### next()로 하나씩 꺼내기

```python
def count():
    yield 1
    yield 2
    yield 3

gen = count()    # 제너레이터 객체 생성

next(gen)   # 1  → yield 1에서 일시정지
next(gen)   # 2  → yield 2에서 일시정지
next(gen)   # 3  → yield 3에서 일시정지
next(gen)   # StopIteration 에러! (더 이상 yield 없음)
```

---

### 실습에서 만든 예제

```python
# 예제 1: 고정값
def count():
    yield 10
    yield 100
    yield 5

gen = count()
next(gen)   # 10
next(gen)   # 100
next(gen)   # 5
next(gen)   # StopIteration ← 더 이상 꺼낼 값이 없음!


# 예제 2: 반복문 + yield
def count_up_to(n):
    i = 1
    while i <= n:
        yield i    # i를 반환하고 일시정지
        i += 1     # next() 호출 시 여기서 재개

gen = count_up_to(3)
next(gen)   # 1
next(gen)   # 2
next(gen)   # 3
next(gen)   # StopIteration
```

### yield의 실행 흐름 시각화

```
count_up_to(3) 실행 흐름:

next(gen) 호출
    → i = 1
    → yield 1  ← 여기서 멈추고 1을 반환

next(gen) 호출
    → i += 1  (i=2, yield 다음 줄부터 재개!)
    → while 2 <= 3  True
    → yield 2  ← 여기서 멈추고 2를 반환

next(gen) 호출
    → i += 1  (i=3)
    → while 3 <= 3  True
    → yield 3  ← 여기서 멈추고 3을 반환

next(gen) 호출
    → i += 1  (i=4)
    → while 4 <= 3  False
    → 함수 종료 → StopIteration 발생!
```

---

### Generator의 장점

```python
# return 방식: 모든 데이터를 메모리에 올려놓음
def get_million_numbers():
    return list(range(1_000_000))   # 100만개를 한 번에 메모리에!

# yield 방식: 필요할 때마다 하나씩 생성
def get_million_numbers():
    for i in range(1_000_000):
        yield i   # 하나씩만 메모리에 올림 ✅
```

> 💡 **언제 Generator를 쓸까?**
> - 데이터가 엄청 많을 때 (메모리 절약)
> - AI 응답을 실시간으로 토큰 단위로 스트리밍할 때 ← 오늘 실습!
> - DB에서 데이터를 조금씩 읽어올 때

---

## 4. LLM 연동 (llama-cpp-python)

### 오늘 한 설치 과정

```bash
# 1. 새 프로젝트 폴더 생성 & 가상환경 만들기
mkdir llama
cd llama
python3.14 -m venv .venv
source .venv/bin/activate

# 2. huggingface_hub 설치 (모델 다운로드 도구)
pip install huggingface_hub

# 3. Hugging Face 로그인
hf auth login
# → 토큰 입력 (huggingface.co/settings/tokens 에서 발급)

# 4. LLaMA 모델 다운로드 (약 808MB)
hf download bartowski/Llama-3.2-1B-Instruct-GGUF \
  Llama-3.2-1B-Instruct-Q4_K_M.gguf \
  --local-dir ./models

# 5. llama-cpp-python 설치 (AI 모델 실행 라이브러리)
pip install llama-cpp-python

# 6. FastAPI 설치
pip install "fastapi[standard]"
```

---

### LLM 관련 용어 정리

| 용어 | 설명 |
|---|---|
| **LLM** | Large Language Model, 대규모 언어 모델 (ChatGPT, LLaMA 등) |
| **GGUF** | 로컬에서 LLM을 실행할 수 있게 압축한 모델 파일 형식 |
| **Q4_K_M** | 모델 압축 방식 (4비트 양자화, 품질/속도 균형) |
| **llama-cpp-python** | C++로 만든 LLM 실행기를 파이썬에서 쓸 수 있게 한 라이브러리 |
| **Hugging Face** | AI 모델을 공유하고 다운로드하는 플랫폼 |
| **n_ctx** | 모델이 한 번에 처리할 수 있는 최대 토큰 수 (컨텍스트 크기) |
| **n_threads** | 모델 실행에 사용할 CPU 스레드 수 |
| **temperature** | 응답의 창의성/무작위성 조절 (높을수록 창의적, 낮을수록 정확) |
| **stream** | 응답을 한 번에 받지 않고 토큰 단위로 실시간으로 받는 것 |

---
### 터미널 실습 결과 분석

```python
# 질문: "파이썬이 뭐야?"
# 응답: "Python"  ← 너무 짧음!

# 질문: "2026년 3월 3일은 무슨요일이야?"
# 응답: "3월 3일은 일요일이야."  ← 틀렸음! (실제로는 화요일)
```

> 💡 **왜 이런 결과가 나왔을까?**
> - `Llama-3.2-1B` 는 파라미터가 **1B(10억개)** 로 비교적 작은 모델
> - 모델이 작을수록 답변 품질이 낮고 할루시네이션(거짓말)이 많음
> - 실제 서비스는 70B, 405B 같은 훨씬 큰 모델을 사용
> - 날짜/요일 같은 계산은 LLM이 원래 잘 못함 (계산기가 아니라 언어 모델이기 때문)

---

## 5. LLM + FastAPI (llama 폴더의 main.py)

### app.state - 서버 전체 공유 데이터

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 LLM 모델 로드
    app.state.llm = Llama(
        model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        n_ctx=4096,       # 최대 4096 토큰
        n_threads=2,      # CPU 2개 사용
        verbose=False,    # 로그 간단하게
        chat_format="llama-3",
    )
    yield
    # 서버 종료 시 정리 (현재는 비어있음)

app = FastAPI(lifespan=lifespan)
```

> 💡 **왜 `app.state`에 저장할까?**
> LLM 모델은 로드하는 데 시간이 오래 걸림 (수십 초!)
> 요청마다 매번 로드하면 너무 느리기 때문에
> 서버 시작 시 한 번만 로드해서 `app.state`에 저장해두고
> 이후 모든 요청에서 꺼내 쓰는 방식!

---

### role 시스템

```python
# LLM에게 역할을 부여하는 방식
messages=[
    {"role": "system", "content": SYSTEM_PROMPT},   # AI의 규칙/성격 설정
    {"role": "user", "content": user_input},         # 사용자 질문
    # {"role": "assistant", "content": "..."}        # 이전 AI 답변 (대화 이어가기)
]
```

| role | 설명 |
|---|---|
| `system` | AI의 규칙, 행동방식, 성격 설정 (사용자에게 안 보임) |
| `user` | 사용자의 질문이나 요청 |
| `assistant` | 이전에 AI가 생성한 답변 (대화 히스토리 유지용) |

---

### SYSTEM_PROMPT

```python
SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "  # 사용자 언어로 답변
    "Do not change the language. "
    "Do not mix languages."
)
```

> 💡 시스템 프롬프트로 AI의 동작 방식을 제어할 수 있음
> "항상 한국어로 답해라", "200자 이내로 답해라" 같은 규칙을 넣을 수 있음

---

### embed=True vs embed=False

```python
user_input: str = Body(..., embed=True)
```

| | `embed=False` (기본) | `embed=True` |
|---|---|---|
| **요청 형식** | `"Python이 뭐야?"` (문자열 그대로) | `{"user_input": "Python이 뭐야?"}` |
| **언제 씀** | 파라미터 하나일 때 | JSON 형태로 명시적으로 받을 때 |

---

## 6. Streaming Response ⭐

### Streaming이란?

> **데이터를 한 번에 다 보내지 않고, 생성되는 즉시 조금씩 전송하는 방식**

```
일반 응답 방식:
클라이언트 → 요청 → 서버 (전체 답변 생성 중...) → 완성 후 한 번에 전송
사용자 입장: 10초 기다렸다가 갑자기 전체 텍스트 등장

스트리밍 방식:
클라이언트 → 요청 → 서버 → "안" → "녕" → "하" → "세" → "요" → ...
사용자 입장: 글자가 실시간으로 타이핑되는 것처럼 보임 ✅
```

---

### Generator + Streaming 연결

```python
async def event_generator():
    llm = request.app.state.llm    # app.state에서 LLM 꺼내오기
    
    response = llm.create_chat_completion(
        messages=[...],
        max_tokens=256,
        temperature=0.7,
        stream=True,               # 스트리밍 모드 켜기
    )

    for chunk in response:         # 응답을 토큰 단위로 순회
        token = chunk["choices"][0]["delta"].get("content")
        if token:
            yield token            # 토큰 하나씩 내보내기 (Generator!)
            await asyncio.sleep(0) # 다른 코루틴에게 실행권 양보
```

#### 흐름 시각화

```
LLM이 "안녕하세요" 생성 중...

chunk 1 → "안" → yield "안" → 클라이언트에게 전송
chunk 2 → "녕" → yield "녕" → 클라이언트에게 전송
chunk 3 → "하" → yield "하" → 클라이언트에게 전송
...
```

---

### StreamingResponse

```python
return StreamingResponse(
    event_generator(),          # Generator 함수 전달
    media_type="text/event-stream",  # SSE(Server-Sent Events) 형식
)
```

| 일반 Response | StreamingResponse |
|---|---|
| 전체 데이터를 한 번에 반환 | Generator로 데이터를 조금씩 반환 |
| 완성 후 전송 | 생성되는 즉시 전송 |
| AI 응답에 부적합 | AI 응답에 최적 ✅ |

---

### `await asyncio.sleep(0)` 왜 쓸까?

```python
yield token
await asyncio.sleep(0)   # 0초 대기 = 실행권 양보
```

> 0초를 기다리는 게 아니라 **다른 코루틴에게 실행권을 잠깐 양보**하는 것!
> 이게 없으면 LLM이 토큰을 생성하는 동안 다른 요청을 처리 못함

---

### curl로 테스트

```bash
curl -N -X POST http://127.0.0.1:8000/chats \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Python이 뭐야?"}'
```

| 옵션 | 설명 |
|---|---|
| `-N` | 버퍼링 없이 스트리밍으로 받기 |
| `-X POST` | POST 요청 |
| `-H` | 헤더 설정 |
| `-d` | 요청 Body 데이터 |

---

## 7. return vs yield 최종 비교

```python
# return → 한 번에 끝, 함수 완전 종료
def make_list():
    return [1, 2, 3]   # 리스트 반환 후 함수 종료

# yield → 일시정지하며 여러 번, 함수 재개 가능
def gen_numbers():
    yield 1   # 1 반환 후 일시정지
    yield 2   # 재개 → 2 반환 후 일시정지
    yield 3   # 재개 → 3 반환 후 일시정지
              # 더 이상 yield 없음 → StopIteration
```

| | `return` | `yield` |
|---|---|---|
| **실행** | 한 번 실행 후 종료 | 일시정지 → 재개 반복 |
| **반환값** | 값 하나 (또는 리스트) | 값 하나씩 순서대로 |
| **메모리** | 전체를 한 번에 | 하나씩만 |
| **함수 상태** | 종료 | 유지 (재개 가능) |
| **사용 예** | 일반 함수 | 스트리밍, 대용량 데이터 |

---

## 8. 오늘 배운 전체 흐름

```
사용자
    │
    │  POST /chats {"user_input": "Python이 뭐야?"}
    ▼
FastAPI (llama/main.py)
    │
    ├─ app.state.llm 으로 LLM 접근 (서버 시작 시 로드된 모델)
    │
    ├─ create_chat_completion(stream=True) 실행
    │
    ├─ event_generator() 실행
    │   ├─ chunk 1 → yield "파" → 클라이언트에게 전송
    │   ├─ chunk 2 → yield "이" → 클라이언트에게 전송
    │   ├─ chunk 3 → yield "썬" → 클라이언트에게 전송
    │   └─ ...
    │
    └─ StreamingResponse로 실시간 전송 ✅
```

---

## 9. 용어 정리

| 용어 | 설명 |
|---|---|
| **Generator** | yield로 값을 하나씩 순서대로 내보내는 함수 |
| **yield** | 값을 반환하고 함수를 일시정지하는 키워드 |
| **next()** | Generator에서 다음 값을 꺼내는 함수 |
| **StopIteration** | Generator에서 더 꺼낼 값이 없을 때 발생하는 에러 |
| **LLM** | 대규모 언어 모델 (ChatGPT, LLaMA 등) |
| **GGUF** | 로컬 실행을 위한 모델 파일 형식 |
| **llama-cpp-python** | 파이썬에서 LLM을 로컬 실행하는 라이브러리 |
| **Hugging Face** | AI 모델 공유 플랫폼 |
| **스트리밍** | 데이터를 조금씩 실시간으로 전송하는 방식 |
| **StreamingResponse** | FastAPI에서 스트리밍 응답을 반환하는 클래스 |
| **SSE** | Server-Sent Events, 서버에서 클라이언트로 실시간 데이터 전송 |
| **app.state** | FastAPI 서버 전체에서 공유하는 데이터 저장 공간 |
| **role** | LLM에서 system/user/assistant 역할 구분 |
| **temperature** | LLM 응답의 창의성 조절값 (0~1) |
| **stream=True** | LLM 응답을 토큰 단위로 스트리밍 받는 옵션 |
| **embed=True** | Body 파라미터를 JSON 키로 감싸서 받는 옵션 |
| **AsyncSession** | 비동기 DB 세션 클래스 |
| **aiosqlite** | SQLite의 비동기 드라이버 |

---

> 📌 **오늘 수업 핵심 한 줄 요약**
> Generator의 yield로 값을 하나씩 내보내고,
> StreamingResponse로 LLM 답변을 실시간 스트리밍하며,
> 비동기 DB 세션으로 모든 API를 async def로 전환해 진짜 비동기 서버를 완성!
