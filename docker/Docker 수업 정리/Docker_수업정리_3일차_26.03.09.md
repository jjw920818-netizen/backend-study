# 🐳 Docker 수업 정리 3일차

> 작성일: 2026년 3월 9일  
> 학습 내용: Redis pub/sub / uuid / 비동기 Redis / FastAPI↔Worker 통신 완성 / Scale-Out 실습 / 터미널 에러 총정리

---

## 📚 오늘 배운 것 한눈에 보기

| 주제 | 설명 |
|---|---|
| **pub/sub** | Redis의 채널 구독/발행 시스템 |
| **uuid** | 요청마다 고유한 ID를 만드는 방법 |
| **aredis (비동기 Redis)** | FastAPI에서 Redis를 비동기로 사용하는 방법 |
| **brpop** | Queue에서 데이터를 꺼낼 때 대기하는 명령어 |
| **전체 흐름 완성** | FastAPI → Queue → Worker → pub/sub → FastAPI |
| **`--scale`** | 컨테이너를 여러 개 띄우는 Scale-Out 실습 |
| **`-u` 옵션** | 파이썬 출력을 즉시 버퍼 없이 보여주는 옵션 |

---

## 1. 오늘 완성한 전체 구조

```
사용자: "파이썬이 뭐야?"  POST /chats
                │
                ▼
╔══════════════════════════════════════════╗
║             FastAPI  (api/)              ║
╠══════════════════════════════════════════╣
║  1)  job_id    발급  (uuid)              ║
║  2)  result:{job_id} 채널 구독             ║
║  3)  inference_queue 에  job  enqueue    ║
║  4)  결과 올 때까지 대기...                  ║
╚═════════════════╦════════════════════════╝
                  ║
                  ║  lpush  (enqueue)
                  ▼
╔══════════════════════════════════════════╗
║         Redis  (Queue + pub/sub)         ║
╠══════════════════════════════════════════╣
║  inference_queue : [ job2 │ job1 ]  ──▶  ║
║  result:abc123   : (구독 대기 중...)        ║
╚═════════════════╦════════════════════════╝
                  ║
                  ║  brpop  (dequeue)
                  ▼
╔══════════════════════════════════════════╗
║            Worker  (worker/)             ║
╠══════════════════════════════════════════╣
║  1)  Queue 에서  job  꺼냄  (brpop)        ║
║  2)  LLaMA 로  AI  추론  🤖                ║
║  3)  result:{job_id}  채널에  publish      ║
╚═════════════════╦════════════════════════╝
                  ║
                  ║  publish  (결과 전송)
                  ▼
╔══════════════════════════════════════════╗
║         FastAPI 가 결과 받아서 응답  ✅       ║
╚══════════════════════════════════════════╝
```

---

## 2. pub/sub - Redis 채널 구독/발행 ⭐

### pub/sub이란?

```
pub/sub = publish / subscribe
  publish   = 발행 (메시지 보내기)
  subscribe = 구독 (채널 듣기)

비유: 유튜브 채널
  채널 구독자 (subscribe) → 새 영상 올라오면 알림받음
  크리에이터  (publish)   → 새 영상 업로드
```

### 동작 방식

```
[ FastAPI ]
  pubsub = redis_client.pubsub()
  await pubsub.subscribe("result:abc123")   ← 채널 구독 (대기)

[ Worker ]
  redis_client.publish("result:abc123", "파이썬은 ...")  ← 채널에 발행

[ FastAPI ]
  async for message in pubsub.listen():
      → "파이썬은 ..." 받아서 사용자에게 응답 ✅
```

---

## 3. uuid - 고유 작업 ID 발급

### 왜 uuid가 필요할까?

```
사용자가 동시에 여러 명 요청하면:

사용자A: "파이썬이 뭐야?"
사용자B: "자바가 뭐야?"

Worker가 처리하고 결과를 돌려줄 때
어떤 결과가 누구 것인지 구분해야 함!
```

```python
import uuid

job_id = str(uuid.uuid4())
# 예: "a3f2c1d4-8b7e-4f2a-9c1d-3e5f7a8b9c0d"
# → 세상에 단 하나뿐인 랜덤 ID
# → 요청마다 다른 ID 발급

channel = f"result:{job_id}"
# → "result:a3f2c1d4-8b7e-4f2a-9c1d-3e5f7a8b9c0d"
# → 이 채널에만 자기 결과가 도착 ✅
```

---

## 4. api/main.py 코드 분석

### 3일차 버전 (한 번에 반환)

```python
import json
import uuid

from redis import asyncio as aredis
from fastapi import FastAPI, Body

redis_client = aredis.from_url("redis://redis:6379", decode_responses=True)

app = FastAPI()

@app.post("/chats")
async def chat_handler(
    question: str = Body(..., embed=True),
):
    job_id = str(uuid.uuid4())
    channel = f"result:{job_id}"

    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    job = {"id": job_id, "question": question}
    await redis_client.lpush("inference_queue", json.dumps(job))

    # 결과를 한 번에 받아서 반환
    result = None
    async for message in pubsub.listen():
        if message["type"] == "message":
            result = message["data"]
            break

    return {"result": result}   # ← 다 완성되면 한 번에 반환
```

### ✅ 오늘 업데이트된 버전 (StreamingResponse - 토큰 단위 스트리밍)

```python
import json
import uuid

from redis import asyncio as aredis
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse   # ← 새로 추가!

redis_client = aredis.from_url("redis://redis:6379", decode_responses=True)

app = FastAPI()

@app.post("/chats")
async def chat_handler(
    question: str = Body(..., embed=True),
):
    job_id = str(uuid.uuid4())
    channel = f"result:{job_id}"

    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    job = {"id": job_id, "question": question}
    await redis_client.lpush("inference_queue", json.dumps(job))

    # 토큰이 올 때마다 즉시 yield (스트리밍!)
    async def event_generator():
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                if data == "[DONE]":   # ← Worker가 완료 신호 보내면 종료
                    break
                yield data             # ← 토큰 하나씩 즉시 전송

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",   # ← SSE 형식
    )
```

### 3일차 vs 오늘 비교

| | 3일차 | 오늘 |
|---|---|---|
| **반환 방식** | 다 완성되면 한 번에 | 토큰 올 때마다 즉시 |
| **사용자 경험** | 전체 완성 후 표시 | ChatGPT처럼 글자마다 표시 |
| **반환 타입** | `{"result": ...}` | `StreamingResponse` |
| **완료 신호** | `break`로 종료 | Worker가 `[DONE]` 보내면 종료 |

### 각 단계 설명

| 단계 | 코드 | 설명 |
|---|---|---|
| **1** | `uuid.uuid4()` | 랜덤 고유 ID 발급 |
| **2** | `pubsub.subscribe(channel)` | Worker가 결과를 보낼 채널 미리 구독 |
| **3** | `lpush("inference_queue", ...)` | Worker가 꺼낼 Queue에 작업 추가 |
| **4** | `event_generator()` | 토큰 올 때마다 yield로 즉시 전송 |
| **5** | `StreamingResponse` | 스트리밍 응답 반환 |

---

## 5. worker/main.py 코드 분석

```python
import json
import redis
from llama_cpp import Llama

# Worker는 동기(sync) Redis 사용 (CPU 작업이라 비동기 필요 없음)
redis_client = redis.from_url("redis://redis:6379", decode_responses=True)

llm = Llama(
    model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=2,
    verbose=False,
    chat_format="llama-3",
)

SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)

def create_response(question: str):
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        max_tokens=256,
        temperature=0.7,
        stream=True,   # ← 오늘 추가! 스트리밍 모드
    )
    return response

def run():
    while True:                                             # 계속 반복
        # [1] Queue에서 job 꺼내기 (없으면 올 때까지 대기)
        _, job_data = redis_client.brpop("inference_queue")
        job: dict = json.loads(job_data)

        # [2] AI 추론 (스트리밍)
        stream = create_response(question=job["question"])

        # [3] 결과를 FastAPI에 토큰 단위로 전달 (publish)
        channel = f"result:{job['id']}"
        for chunk in stream:
            token = chunk["choices"][0]["delta"].get("content")
            if token:
                redis_client.publish(channel, token)   # ← 토큰 하나씩 publish
        redis_client.publish(channel, "[DONE]")        # ← 완료 신호

if __name__ == "__main__":
    run()
```

### api vs worker Redis 사용 비교

```
【 api/main.py 】
from redis import asyncio as aredis
redis_client = aredis.from_url(...)   ← 비동기 Redis ✅
await redis_client.lpush(...)         ← await 필요
async for message in pubsub.listen()  ← 비동기 순회

이유: FastAPI는 async def를 써서 비동기 환경이기 때문


【 worker/main.py 】
import redis
redis_client = redis.from_url(...)    ← 동기 Redis ✅
_, job = redis_client.brpop(...)      ← await 없음

이유: Worker는 CPU bound 작업 (LLaMA 추론)이라
     비동기로 해도 의미가 없기 때문
```

---

## 6. brpop - 대기하며 꺼내기

```python
_, job_data = redis_client.brpop("inference_queue")
```

| 명령어 | 설명 |
|---|---|
| `rpop` | Queue 오른쪽에서 꺼냄. Queue가 비어있으면 None 반환 |
| `brpop` | Queue 오른쪽에서 꺼냄. **Queue가 비어있으면 올 때까지 대기** (b = blocking) |

```
brpop 동작:

Queue가 비어있음
    → Worker: "기다릴게..."  (무한 대기)

FastAPI가 lpush로 job 추가
    → Worker: "왔다!" 즉시 꺼내서 처리 ✅
```

```python
_, job_data = redis_client.brpop("inference_queue")
# ↑
# brpop은 (키이름, 값) 튜플을 반환
# 키이름은 필요 없어서 _ 로 버림
# job_data만 사용
```

---

## 7. json.dumps / json.loads

```python
# Redis는 문자열만 저장 가능 → 딕셔너리를 JSON 문자열로 변환

# 저장할 때 (딕셔너리 → JSON 문자열)
job = {"id": job_id, "question": "파이썬이 뭐야?"}
await redis_client.lpush("inference_queue", json.dumps(job))
# → '{"id": "abc123", "question": "파이썬이 뭐야?"}'

# 꺼낼 때 (JSON 문자열 → 딕셔너리)
_, job_data = redis_client.brpop("inference_queue")
job: dict = json.loads(job_data)
# → {"id": "abc123", "question": "파이썬이 뭐야?"}
```

---

## 8. `-u` 옵션 - 파이썬 출력 즉시 보기

### worker/Dockerfile

```dockerfile
FROM python:3.13
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "-u", "main.py"]
#                ^^^
#                unbuffered mode
```

```
기본 파이썬:
  print("Worker Start")
  → 버퍼에 쌓아뒀다가 나중에 한 번에 출력
  → docker logs 봐도 안 보임 ❌

-u 옵션:
  print("Worker Start")
  → 즉시 출력
  → docker logs에서 바로 확인 가능 ✅
```

---

## 9. docker logs - 컨테이너 로그 확인 ⭐

> **실행 중인 컨테이너에서 출력된 내용(print, 에러 등)을 보는 명령어**  
> 에러가 났을 때, 잘 돌아가고 있는지 확인할 때 제일 자주 쓰는 명령어

### 기본 구조

```bash
docker logs [옵션] 컨테이너이름
#           ^^^^^^ ^^^^^^^^^^^^^
#           선택   필수
```

### 자주 쓰는 패턴

```bash
# 지금까지 쌓인 로그 전체 출력
docker logs docker-worker-1

# 실시간으로 계속 출력 (-f = follow, 스트리밍)
docker logs docker-worker-1 -f
#                           ^^
#                           새 로그가 생기면 계속 출력 (Ctrl+C 로 종료)

# 마지막 20줄만 출력 (로그가 너무 많을 때)
docker logs docker-worker-1 --tail 20
```

### 왜 쓰냐?

```
컨테이너는 백그라운드(-d)로 실행됨
    → 출력이 터미널에 안 보임

docker logs로 확인해야 함!

예: Worker가 에러났는지 확인
    docker logs docker-worker-1
    → "Traceback ..." 에러 발견 → 코드 수정

예: Worker가 잘 시작됐는지 확인
    docker logs docker-worker-1 -f
    → "Worker Start" 출력 확인 ✅
```

### 오늘 실습에서 실제로 쓴 것들

```bash
# Worker가 왜 안 되는지 확인
docker logs docker-worker-1
# → "form_url AttributeError" 발견

# Worker 실시간 모니터링
docker logs docker-worker-1 -f
# → "llama_context: n_ctx_per_seq..." 출력 확인

# API 서버 시작 확인
docker logs docker-api-1
# → "Application startup complete." 확인 ✅
```

### 에러: `-f`를 이름에 붙여버린 경우

```bash
# 틀림 ❌
docker logs docker-worker-1-f
# Error: No such container: docker-worker-1-f
# (컨테이너 이름에 -f가 포함된 걸로 인식)

# 맞음 ✅
docker logs docker-worker-1 -f
#                           ^ 띄어쓰기로 구분!
```

---

## 10. docker exec - 컨테이너 내부 접속 ⭐

> **실행 중인 컨테이너 안에 들어가서 명령어를 직접 실행하는 명령어**  
> 컨테이너 내부 파일 확인, 직접 파이썬 실행, 디버깅할 때 사용

### 기본 구조

```bash
docker exec [옵션] 컨테이너이름 실행할명령어
#           ^^^^^^ ^^^^^^^^^^^^^ ^^^^^^^^^^^
#           선택   필수          필수
```

### 옵션 설명

```bash
docker exec -it docker-api-1 bash
#           ^^
#           -i : interactive (입력을 받을 수 있게)
#           -t : tty (터미널처럼 보이게)
#           → 둘 다 써야 "터미널처럼" 안에서 명령어 입력 가능

#                            ^^^^
#                            bash : 배시 쉘 실행
#                            → 컨테이너 내부 터미널로 진입
```

### 실제 사용 흐름

```bash
# 1) 컨테이너 내부로 진입
docker exec -it docker-api-1 bash

# 2) 이제 컨테이너 내부 터미널
root@4bb22adb1ea6:/app#    ← 여기가 컨테이너 안!
#   ^^^^^^^^^^^^^  ^^^^
#   컨테이너 ID   현재 경로 (/app = WORKDIR로 지정한 곳)

# 3) 내부에서 원하는 명령어 실행
root@4bb22adb1ea6:/app# python
root@4bb22adb1ea6:/app# ls
root@4bb22adb1ea6:/app# pip list

# 4) 나가기
exit   또는   Ctrl+D
```

### 왜 쓰냐?

```
컨테이너는 독립된 환경
    → 내 컴퓨터에서 바로 파이썬 실행해도 컨테이너 환경이 아님
    → 컨테이너 안에서 테스트하려면 exec로 들어가야 함

주요 사용 상황:

1) 직접 파이썬으로 Redis 연결 테스트
   → exec로 들어가서 python 실행 후 테스트

2) 파일이 제대로 복사됐는지 확인
   → exec로 들어가서 ls, cat으로 확인

3) 패키지가 설치됐는지 확인
   → exec로 들어가서 pip list 확인

4) DB 테이블 직접 생성 (이전 2일차 에러 해결할 때)
   → exec로 MySQL 컨테이너 접속 후 SQL 실행
```

### 오늘 실습에서 실제로 쓴 것들

```bash
# API 컨테이너 내부 접속
docker exec -it docker-api-1 bash

# 내부에서 Redis 연결 테스트
>>> import redis
>>> redis_client = redis.from_url("redis://redis:6379", decode_responses=True)
>>> redis_client.ping()    # → True ✅  (Redis 연결 확인!)

# pub/sub 테스트
>>> redis_client.publish("youtube", "hello")   # → 0 (구독자 없음)
>>> pubsub = redis_client.pubsub()
>>> pubsub.subscribe("youtube")                # 구독 등록
```

### docker exec vs docker logs 비교

```
docker logs 컨테이너이름
    → 컨테이너가 출력한 내용을 밖에서 구경
    → 내부 진입 X

docker exec -it 컨테이너이름 bash
    → 컨테이너 안으로 직접 들어감
    → 내부에서 명령어 직접 실행 ✅
```

---

## 11. Scale-Out 실습 - worker 여러 개 띄우기

```bash
docker compose up -d --scale worker=2
```

```
결과:
docker-worker-1  (기존)
docker-worker-2  (새로 추가) ✅

→ 두 Worker가 동시에 Queue 대기
→ job이 들어오면 먼저 꺼낸 Worker가 처리
→ 두 개의 AI 추론이 병렬로 처리 가능
```

```
Queue: [ job1 | job2 | job3 ]

Worker-1: job1 꺼내서 처리 중
Worker-2: job2 꺼내서 처리 중
→ 동시에 2개 처리 ✅ (단, 각 Worker는 한 번에 1개만)
```

---

## 12. Redis 실습 (컨테이너 내부에서)

```bash
docker exec -it docker-api-1 bash
python
```

```python
import redis
redis_client = redis.from_url("redis://redis:6379", decode_responses=True)

# 연결 확인
redis_client.ping()       # → True ✅

# 데이터 저장/조회/삭제
redis_client.set("name", "alex")   # → True
redis_client.get("name")           # → "alex"
redis_client.get("age")            # → None (없는 키)
redis_client.delete("name")        # → 1 (삭제된 개수)

# pub/sub 테스트
redis_client.publish("youtube", "hello")   # → 0 (구독자 없어서 0)

pubsub = redis_client.pubsub()
pubsub.subscribe("youtube")        # 채널 구독
```

---

## 13. 터미널 에러 총정리 🔧

---

### 에러 1: `volumes must be a array`

```
validating docker-compose.yml: services.worker.volumes must be a array
```

**원인:** docker-compose.yml에서 volumes 항목 앞에 `-` 가 빠짐  
**수정:**
```yaml
# 틀림 ❌
volumes:
  ./worker:/app

# 맞음 ✅
volumes:
  - ./worker:/app
```

---

### 에러 2: `[python,: not found`

```
/bin/sh: 1: [python,: not found
```

**원인:** Dockerfile CMD를 문자열(shell 형식)로 쓰면 안 됨  
**수정:**
```dockerfile
# 틀림 ❌
CMD "python -u main.py"

# 맞음 ✅  (반드시 배열 형식으로)
CMD ["python", "-u", "main.py"]
```

---

### 에러 3: `coroutine was never awaited` ⭐

```
RuntimeWarning: coroutine 'Redis.execute_command' was never awaited
TypeError: cannot unpack non-iterable coroutine object
```

**원인:** Worker(동기 함수)에서 비동기 Redis(`aredis`)를 사용  
**핵심:** `def run()` 은 동기 함수라 `await` 사용 불가 → 비동기 Redis를 쓰면 coroutine 객체가 그대로 반환됨

```python
# 틀림 ❌  (비동기 Redis를 동기 함수에서 사용)
from redis import asyncio as aredis
redis_client = aredis.from_url(...)
_, job_data = redis_client.brpop(...)   # coroutine 반환 → 언패킹 불가

# 맞음 ✅  (Worker는 동기 Redis 사용)
import redis
redis_client = redis.from_url(...)
_, job_data = redis_client.brpop(...)   # 바로 값 반환
```

```
정리:
  FastAPI  → async def  → 비동기 Redis (aredis) ✅
  Worker   → def        → 동기 Redis   (redis)  ✅
```

---

## 14. 오늘 에러 흐름 타임라인

```
volumes 형식 오류  → validating error  ❌
       ↓ 수정
CMD 형식 오류      → [python,: not found ❌
       ↓ 수정
비동기/동기 Redis 혼용 → coroutine 에러  ❌
       ↓ 수정 (Worker를 동기 Redis로 교체)
       ↓
전체 정상 동작 ✅
       ↓
docker compose up -d --scale worker=2  →  Scale-Out 성공! 🎉
```

---

## 15. 용어 정리

| 용어 | 설명 |
|---|---|
| **pub/sub** | 채널에 발행(publish)하고 구독(subscribe)하는 메시지 패턴 |
| **publish** | 채널에 메시지를 보내는 것 |
| **subscribe** | 채널을 구독해서 메시지를 받는 것 |
| **uuid** | 세상에 단 하나뿐인 랜덤 고유 식별자 |
| **brpop** | blocking rpop, Queue가 빌 때 올 때까지 대기하며 꺼내기 |
| **lpush** | Queue 왼쪽에 데이터 추가 (enqueue) |
| **json.dumps** | 딕셔너리 → JSON 문자열 변환 |
| **json.loads** | JSON 문자열 → 딕셔너리 변환 |
| **aredis** | `from redis import asyncio as aredis`, 비동기 Redis |
| **동기 Redis** | `import redis`, 일반 동기 방식 |
| **`-u`** | 파이썬 unbuffered 모드, 출력 즉시 표시 |
| **`--scale`** | Docker Compose에서 특정 서비스를 N개로 늘리기 |
| **`_`** | 파이썬에서 필요없는 변수를 버릴 때 쓰는 관례 |
| **`decode_responses=True`** | Redis에서 bytes가 아닌 str로 받기 |

---

> 📌 **오늘 수업 핵심 한 줄 요약**  
> FastAPI는 비동기 Redis로 Queue에 job을 넣고 pub/sub으로 결과를 기다리고,  
> Worker는 동기 Redis로 brpop으로 job을 하나씩 꺼내 AI 추론 후 publish로 결과를 돌려주며,  
> `--scale worker=2`로 Worker를 여러 개 띄워 처리량을 늘릴 수 있다!

---

## 🎯 오늘 수업 목표 달성 확인

> **Docker Compose를 활용해서 컨테이너를 관리하는 방법**  
> **Redis를 활용하여 추론 서버의 동시성 문제를 해결하는 방법**

### ✅ Docker Compose로 컨테이너 관리 (2일차 → 3일차)

| 단계 | 배운 것 |
|---|---|
| **2일차** | `docker-compose.yml` 작성, 4개 컨테이너 한 번에 실행/종료, Volume 설정 |
| **3일차** | 에러 수정하며 compose 반복 실습, `--scale worker=2` 로 Scale-Out |

```
docker compose up -d --build   → api / worker / db / redis 한 번에 실행 ✅
docker compose down            → 전체 종료 ✅
docker compose up -d --scale worker=2  → worker 컨테이너 2개로 Scale-Out ✅
```

### ✅ Redis로 동시성 문제 해결 (2일차 개념 → 3일차 코드 완성)

| 단계 | 배운 것 |
|---|---|
| **2일차** | 동시성 문제가 뭔지, Queue 개념, Redis 역할 이해 |
| **3일차** | `lpush` → `brpop` → `publish` → `subscribe` 실제 코드로 구현 |

```
동시성 문제 해결 전체 흐름:

FastAPI           Redis (Queue)          Worker
   │                   │                    │
   │  lpush(enqueue)   │                    │
   │──────────────────▶│                    │
   │                   │  brpop(dequeue)    │
   │                   │───────────────────▶│
   │                   │                    │ AI 추론
   │                   │    publish(결과)   │
   │                   │◀───────────────────│
   │  subscribe(수신)  │                    │
   │◀──────────────────│                    │
   │                   │                    │
사용자에게 응답 ✅
```
