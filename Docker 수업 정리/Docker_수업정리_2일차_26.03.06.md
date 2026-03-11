# 🐳 Docker 수업 정리 2일차

> 작성일: 2026년 3월 6일
> 학습 내용: Docker Volume / MySQL 데이터 영속성 / Volume Mount / Worker 분리 / Redis / Queue / 동시성 문제

---

## 📚 오늘 배운 것 한눈에 보기

| 주제 | 설명 |
|---|---|
| **RAM과 컨테이너** | 컨테이너 실행 = RAM에 올라감, 종료 = RAM에서 내려감 |
| **데이터 유실 문제** | 컨테이너 종료 시 DB 데이터가 사라지는 문제 |
| **Docker Volume** | 컨테이너 밖에 데이터를 저장해서 유지하는 방법 |
| **Volume Mount** | 코드 수정 시 빌드 없이 바로 반영하는 개발 방법 |
| **동시성 문제** | AI 모델에 동시에 요청이 오면 발생하는 문제 |
| **Queue** | 작업을 순서대로 쌓아두고 하나씩 처리하는 구조 |
| **Redis** | Queue 역할을 하는 메모리 기반 빠른 데이터 저장소 |
| **Worker 분리** | AI 추론을 별도 컨테이너로 분리하는 구조 |

---

## 1. RAM과 Docker 컨테이너의 관계

```
컨테이너 실행 (docker compose up)
    → Host OS의 RAM에 올라감 (메모리 점유 시작)

컨테이너 종료 (docker compose down)
    → Host OS의 RAM에서 내려감 (메모리 해제)
```

> 💡 **Host OS란?**
> 도커가 실행되고 있는 실제 내 컴퓨터 운영체제 (Mac, Windows, Linux)
> 도커 컨테이너들은 Host OS 위에서 동작해

---

## 2. MySQL 컨테이너의 데이터 유실 문제 ⚠️

### 문제 상황

```
docker compose up
    → MySQL 컨테이너 시작
    → DB에 데이터 입력 (alex, bob, chris)

docker compose down
    → 컨테이너 종료 및 삭제

docker compose up   ← 다시 시작
    → 데이터가 사라짐! ❌
```

### 왜 데이터가 사라질까?

```
MySQL이 데이터를 저장하는 곳:
    컨테이너 내부의 /var/lib/mysql 폴더

컨테이너가 삭제되면:
    컨테이너 내부 파일도 전부 같이 삭제됨
    → 데이터 유실! ❌
```

---

## 3. Docker Volume - 데이터 영속성 ⭐

### Volume이란?

> **컨테이너 내부가 아닌 외부 저장소(볼륨)에 데이터 디렉토리를 연결하는 방식**
> 컨테이너가 삭제되어도 데이터 볼륨은 그대로 유지됨

### Volume 없을 때 vs 있을 때

```
❌ Volume 없을 때:

  ┌──────────────────────┐
  │  컨테이너             │
  │  /var/lib/mysql      │  ← 컨테이너 삭제 시 데이터도 같이 삭제
  └──────────────────────┘


✅ Volume 있을 때:

  ┌──────────────────────┐        ┌──────────────────────┐
  │  컨테이너             │        │  Host OS (내 컴퓨터)   │
  │  /var/lib/mysql ─────┼──────▶ │  docker_db_data      │
  └──────────────────────┘        └──────────────────────┘
  컨테이너 삭제해도 →                볼륨은 그대로 유지 ✅
```

### docker-compose.yml 설정

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: 1234
      MYSQL_DATABASE: oz
    volumes:
      - db_data:/var/lib/mysql   # 컨테이너 내부 경로를 볼륨에 연결
      #  ^^^^^^^  ^^^^^^^^^^^^^^
      #  볼륨이름  컨테이너 안의 경로 (MySQL 데이터 저장 위치)

volumes:
  db_data:   # 볼륨 이름 선언 (Host OS에 실제로 저장됨)
```

### docker volume 명령어

```bash
docker volume ls              # 볼륨 목록 보기
docker volume inspect 볼륨명   # 볼륨 상세 정보
docker volume rm 볼륨명        # 볼륨 삭제
docker volume prune           # 사용 안 하는 볼륨 전부 삭제
```

---

## 4. Volume Mount - 팀 프로젝트에서 꼭 써야 하는 이유 ⭐

Volume은 두 가지 목적으로 사용한다. **DB 데이터 보존**과 **코드 실시간 반영**. 팀 프로젝트에서 둘 다 설정해두면 개발이 훨씬 편해진다.

---

### 🗄️ DB Volume — 데이터 영속성 보장

팀원 중 누군가 `docker compose down`을 해도 DB 데이터가 사라지지 않는다.
볼륨 설정 한 줄로 전원이 같은 데이터를 유지한 채 개발할 수 있다.

```yaml
services:
  db:
    image: mysql:8.0
    volumes:
      - db_data:/var/lib/mysql   # ← 이 한 줄로 데이터 영구 보존

volumes:
  db_data:
```

```
❌ 볼륨 없으면:
   팀원A가 docker compose down
   → 다음에 up 할 때 테이블도 다시 만들고, 데이터도 다시 넣어야 함

✅ 볼륨 있으면:
   docker compose down 해도
   → 다시 up 하면 데이터 그대로 ✅
```

---

### 💻 Code Volume (Mount) — 빌드 없이 코드 수정 반영

내 컴퓨터의 코드 폴더를 컨테이너 안에 직접 연결한다.
저장하면 즉시 반영되기 때문에 코드 수정마다 빌드를 기다릴 필요가 없다.

```yaml
services:
  api:
    build: ./api
    volumes:
      - ./api:/app   # 내 컴퓨터 ./api 폴더 ↔ 컨테이너 /app 실시간 동기화
```

```
❌ Volume Mount 없으면:

  코드 수정(v1) → docker compose up -d --build (20초 대기)
  코드 수정(v2) → 또 빌드 (20초 대기) ❌
  코드 수정(v3) → 또 빌드 (20초 대기) ❌


✅ Volume Mount 있으면:

  docker compose up -d --build  (최초 1회만!)

  코드 수정(v2) → 저장 → 즉시 반영 ✅
  코드 수정(v3) → 저장 → 즉시 반영 ✅
  코드 수정(v4) → 저장 → 즉시 반영 ✅
```

> 💡 **`--build` 옵션이란?**
> `docker compose up -d --build` = 이미지를 새로 빌드하고 컨테이너 실행
> 코드 수정 후 반영하려면 이 명령어로 한 번에 처리 가능

---

## 5. 파일 구조 변경 (api / worker 분리)

```
📁 docker
├── api/                   ← FastAPI 서버
│   ├── Dockerfile
│   ├── main.py
│   ├── database.py
│   └── requirements.txt   (fastapi, sqlalchemy, pymysql, redis)
│
├── worker/                ← AI 추론 워커 (오늘 새로 추가)
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt   (llama-cpp-python, redis)
│
└── docker-compose.yml     ← 두 서비스를 함께 관리
```

### worker/Dockerfile

```dockerfile
FROM python:3.13          # slim 아닌 full 버전 (LLaMA 빌드에 필요한 도구 포함)
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

> 💡 **api는 `python:3.13-slim`, worker는 `python:3.13`인 이유**
> `slim` = 불필요한 것 제거한 가벼운 버전 (용량 작음)
> `python:3.13` = 전체 버전 (용량 큼)
> LLaMA 같은 라이브러리는 C++ 빌드 도구가 필요해서 full 버전을 써야 함

### worker/main.py

```python
import redis

redis_client = redis.from_url("redis://redis:6379", decode_responses=True)

def run():
    pass   # 나중에 AI 추론 로직이 들어올 자리

if __name__ == "__main__":
    run()
```

#### `if __name__ == "__main__":` 란?

```python
# python main.py로 직접 실행했을 때만 run() 호출
# 다른 파일에서 import 했을 때는 run() 호출 안 됨

if __name__ == "__main__":
    run()
```

> `__name__`은 파이썬이 자동으로 설정해주는 변수
> 직접 실행하면 `__name__ = "__main__"`
> import 되면 `__name__ = "모듈이름"`

---

## 6. 동시성 문제 ⭐

### AI 모델의 특성

> **AI 모델이 추론 중일 때 다른 요청을 주면 안 됨!**
> 동시에 여러 추론 요청이 오면 상태가 혼합되어 이상한 결과를 만들어냄

```
사용자A: "파이썬이 뭐야?"  ──┐
사용자B: "자바가 뭐야?"   ──┘ 동시에 추론 시작

AI 모델: "파이썬이 뭐야 자바가..."  ← 뒤섞인 이상한 답변! ❌
```

### 문제 정의

```
1. 사용자는 동시에 요청할 수 있어야 한다  ← 사용자 입장에서 당연한 것
2. AI 추론은 한 번에 하나씩만 처리해야 한다  ← AI 모델의 특성

→ 이 두 가지를 동시에 만족해야 함!
```

---

## 7. Queue — 동시성 문제 해결 방법 ⭐

### Queue란?

> **작업을 순서대로 쌓아두고, 하나씩 처리하기 위한 구조**

```
비유: 은행 번호표 시스템

고객A ──┐
고객B ──┼──→ 대기열(Queue) ──→ 창구(AI 모델) 하나씩 처리
고객C ──┘

→ 고객은 동시에 번호표 뽑을 수 있음 ✅
→ 창구는 한 번에 한 명씩만 처리 ✅
```

### 수업 자료 다이어그램

```
                  ┌─────────┐
                  │  Task   │  ← 여러 요청이 쌓임
                  ├─────────┤
 ┌──────────┐     │  Task   │                    ┌──────────────────┐
 │          │     │         │       Task          │                  │
 │ FastAPI  │ ──▶ │  Queue  │ ──────────────────▶ │ Inference Worker │
 │          │     │         │                    │                  │
 └──────────┘     └─────────┘                    └──────────────────┘
               enqueue ↑              dequeue ↑
           (작업을 Queue에 넣기)   (Queue에서 하나씩 꺼내기)
```

### FastAPI + Queue + AI 모델 전체 구조

```
사용자A ──┐
사용자B ──┼──→ FastAPI 서버 ──→ Queue(Redis) ──→ Worker(AI 모델)
사용자C ──┘      요청 받고            ↑               하나씩 처리
                  바로 응답      작업 쌓임

→ FastAPI는 요청을 Queue에 넣고 바로 응답 ✅
→ Worker는 Queue에서 하나씩 꺼내서 추론 ✅
```

---

## 8. Redis ⭐

### Redis란?

> **메모리 기반의 빠른 데이터 저장소**
> key-value 형태로 데이터를 저장하고 Queue, 캐시, pub/sub 기능을 제공

```python
# Redis는 비유하면 "엄청 빠른 초소형 데이터베이스"
# key: value 형태로 저장
redis_client.set("name", "alice")   # 저장
redis_client.get("name")            # → "alice" 조회
```

### MySQL vs Redis 비교

| | MySQL | Redis |
|---|---|---|
| **저장 위치** | SSD (디스크) | RAM (메모리) |
| **속도** | 비교적 느림 | 매우 빠름 ✅ |
| **데이터 유지** | 영구 저장 | 기본적으로 휘발성 |
| **용도** | 영구 데이터 저장 | 캐시, Queue, 임시 데이터 |
| **형태** | 테이블 (행/열) | key-value |

### Redis의 Queue 역할

```python
# FastAPI가 요청을 받으면:
redis_client.lpush("queue", "사용자A의 요청")  # Queue에 추가

# Worker가 계속 Queue를 확인:
job = redis_client.brpop("queue")  # Queue에서 하나 꺼내기
# → AI 추론 실행
# → 완료 후 다음 꺼내기
```

```
Queue 상태:
┌──────────────────────────────────────────┐
│  사용자C 요청 │ 사용자B 요청 │ 사용자A 요청  │
└──────────────────────────────────────────┘
                                        ↑
                              Worker가 꺼내서 처리
                              (먼저 들어온 것부터)
```

### Redis 연결 코드

```python
import redis

# redis://서비스이름:포트번호
redis_client = redis.from_url("redis://redis:6379", decode_responses=True)
#                                      ^^^^^
#                      docker-compose.yml에서 정의한 서비스 이름
```

> 💡 **왜 `localhost`가 아니라 `redis`일까?**
> Docker Compose 안의 컨테이너들은 서비스 이름으로 서로를 찾음
> `redis`는 docker-compose.yml에서 정의한 서비스 이름!

---

## 9. api / worker 분리 이유 ⭐

### 왜 쪼갰냐?

```
❌ 하나의 컨테이너에 FastAPI + AI 모델 같이 있으면:

  ┌─────────────────────────────┐
  │  컨테이너                    │
  │  FastAPI 요청 처리 → CPU 사용 │
  │  AI 모델 추론 중 → CPU 100%  │ ← 둘이 CPU를 나눠써서 둘 다 느려짐 ❌
  └─────────────────────────────┘


✅ 컨테이너 분리하면:

  ┌────────────────┐     ┌────────────────────┐
  │  api 컨테이너   │     │  worker 컨테이너     │
  │  FastAPI만 처리 │     │  AI 추론만 처리      │
  │  CPU: 가볍게   │     │  CPU: 100% 추론전용  │ ✅
  └────────────────┘     └────────────────────┘
```

하나의 도커를 쓰더라도 컨테이너로 분리하면 독립된 실행환경을 나누는 효과를 줄 수 있다.

### 각각 다른 CPU / 메모리 사용

```
api 컨테이너:
    → FastAPI 요청 처리 (네트워크 I/O 위주)
    → RAM 적게 사용
    → CPU 적게 사용

worker 컨테이너:
    → LLaMA 추론 (무거운 CPU bound 작업)
    → RAM 많이 사용 (모델 로딩)
    → CPU 100% 사용 가능
```

---

## 10. Scale-Out (수평 확장)

```
Scale-Up (수직 확장):                    Scale-Out (수평 확장):
CPU 2개 → 8개                           서버 1개 → 여러 개
RAM 16GB → 64GB                        요청 많으면 컨테이너 더 띄우기

비용 많이 들고 한계가 있음 ❌              비교적 저렴하고 유연함 ✅
```

```
도커로 Scale-Out 하는 방법:

FastAPI 컨테이너 1 ──┐
FastAPI 컨테이너 2 ──┼──→ Redis Queue ──→ Worker 1개 (추론은 하나씩)
FastAPI 컨테이너 3 ──┘

→ 사용자 요청은 여러 FastAPI가 나눠서 받음 ✅
→ 추론은 Worker 1개가 순서대로 처리 ✅
```

---

## 11. 쿠버네티스 (Kubernetes / K8S)

```
Docker Compose: 내 컴퓨터 1대에서 여러 컨테이너 관리
Kubernetes:     여러 컴퓨터(서버)에서 컨테이너를 자동으로 관리

실제 서비스 규모:
서버 100대에서 컨테이너 1000개를 자동으로 띄우고,
죽으면 살리고, 트래픽 많으면 자동으로 늘리고 → 이게 K8S
```

> 지금 단계에서는 "Docker Compose의 업그레이드 버전" 정도로만 알아둬도 충분!

---

## 12. 터미널 에러 분석

### 에러 1: Table doesn't exist

```
pymysql.err.ProgrammingError: (1146, "Table 'oz.user' doesn't exist")
```

DB 컨테이너는 떴지만 테이블이 없어서 발생.
`docker exec -it docker-db-1 bash` 로 들어가서 테이블 직접 생성해서 해결.

---

### 에러 2: requirementstxt (오타)

```
ERROR: Could not open requirements file: 'requirementstxt'
```

Dockerfile에서 `requirements.txt`의 `.`이 빠진 오타. 수정 후 해결.

---

### 에러 3: ports are not available

```
Error response from daemon: ports are not available: TCP 0.0.0.0:3306
```

내 컴퓨터에 MySQL이 이미 3306 포트를 쓰고 있어서 충돌.
`brew services stop mysql`로 로컬 MySQL 종료 후 해결.

---

### 에러 4: volumes must be a array

```
validating docker-compose.yml: services.api.volumes must be a array
```

yml 파일에서 volumes 형식이 잘못된 것 (들여쓰기 또는 형식 오류). 수정 후 해결.

---

## 13. 오늘 배운 전체 구조

```
사용자 요청
    ↓
┌──────────────────┐
│  FastAPI 컨테이너  │  ← 요청 받고 Queue에 넣음
└────────┬─────────┘
         │ enqueue
         ▼
┌──────────────────┐
│  Redis (Queue)   │  ← 작업을 순서대로 쌓아둠
└────────┬─────────┘
         │ dequeue (하나씩)
         ▼
┌──────────────────┐
│  Worker 컨테이너   │  ← AI 추론 처리
└──────────────────┘

+ MySQL 컨테이너  ← DB Volume으로 데이터 영구 보존
+ Volume Mount   ← 코드 수정 시 빌드 없이 즉시 반영
```

---

## 14. 용어 정리

| 용어 | 설명 |
|---|---|
| **Host OS** | 도커가 실행되는 실제 내 컴퓨터 운영체제 |
| **Volume** | 컨테이너 외부에 데이터를 저장하는 공간 |
| **데이터 영속성** | 컨테이너를 삭제해도 데이터가 유지되는 것 |
| **Volume Mount** | 컨테이너의 폴더를 외부 폴더/볼륨에 연결하는 것 |
| **동시성 문제** | 여러 요청이 동시에 오면서 발생하는 충돌 문제 |
| **Queue** | 작업을 순서대로 쌓아두고 하나씩 처리하는 자료구조 |
| **enqueue** | Queue에 작업을 넣는 것 |
| **dequeue** | Queue에서 작업을 꺼내는 것 |
| **Redis** | 메모리 기반의 빠른 key-value 데이터 저장소 |
| **Worker** | Queue에서 작업을 꺼내서 처리하는 프로세스 |
| **pub/sub** | 발행/구독 모델, 메시지를 보내고 받는 Redis 기능 |
| **Scale-Out** | 서버 수를 늘려서 처리량을 높이는 수평 확장 |
| **Scale-Up** | 서버 성능을 높이는 수직 확장 (CPU, RAM 증가) |
| **K8S** | Kubernetes, 여러 서버에서 컨테이너를 자동 관리 |
| **`--build`** | `docker compose up` 시 이미지를 새로 빌드하는 옵션 |
| **`if __name__ == "__main__"`** | 직접 실행할 때만 코드를 실행하게 하는 파이썬 문법 |

---

> 📌 **오늘 수업 핵심 한 줄 요약**
> 컨테이너가 삭제되면 데이터가 사라지니까 Volume으로 영속성을 보장하고,
> AI 추론의 동시성 문제는 Queue(Redis) + Worker 분리로 해결하며,
> api/worker를 독립된 컨테이너로 나눠 각자 CPU를 온전히 사용!
