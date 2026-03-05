# 🐳 Docker 수업 정리 1일차

> 작성일: 2026년 3월 5일
> 학습 내용: Docker 개념 / Dockerfile / 이미지 빌드 / 컨테이너 실행 / Docker Compose

---

## 📚 오늘 배운 것 한눈에 보기

| 주제 | 설명 |
|---|---|
| **Docker란** | 내 코드를 어디서든 똑같이 실행할 수 있게 포장하는 기술 |
| **Image** | 컨테이너를 만들기 위한 설계도 (읽기 전용) |
| **Container** | Image로 만든 실제 실행 중인 환경 |
| **Dockerfile** | Image를 만드는 방법을 적은 레시피 파일 |
| **docker build** | Dockerfile로 Image를 만드는 명령어 |
| **docker run** | Image로 Container를 실행하는 명령어 |
| **docker ps** | 실행 중인 Container 목록 보기 |
| **Docker Compose** | 여러 Container를 한 번에 관리하는 도구 |

---

## 1. Docker가 왜 필요할까?

### Docker 없이 서버에 배포할 때 문제

```
내 컴퓨터:
- Python 3.13
- FastAPI 0.135
- Mac OS

서버:
- Python 3.9
- 라이브러리 버전 다름
- Linux

→ 내 컴퓨터에서는 잘 됐는데 서버에서 에러! ❌
  "내 컴퓨터에서는 되는데..." 문제
```

### Docker로 해결

```
내 코드 + 파이썬 버전 + 라이브러리를
하나의 "박스(Container)"에 포장!

→ 어떤 컴퓨터에서 실행해도 똑같이 동작 ✅
→ Mac, Linux, Windows, 서버 어디서든!
```

> 💡 **비유로 이해하기**
> Docker = 음식 밀키트
> 밀키트(Container)를 열면 재료, 소스, 레시피가 다 들어있음
> 어느 주방(서버)에서 만들어도 똑같은 음식이 나옴!

---

## 2. 핵심 용어: Image vs Container

| | Image | Container |
|---|---|---|
| **비유** | 붕어빵 틀 (설계도) | 실제 붕어빵 (실행 중인 것) |
| **비유2** | 프로그램 설치 파일 (.exe) | 실행 중인 프로그램 |
| **특징** | 읽기 전용, 변경 불가 | 실행 중, 여러 개 만들 수 있음 |
| **만드는 법** | `docker build` | `docker run` |

```
Dockerfile → (docker build) → Image → (docker run) → Container
   레시피          요리 시작       완성된 요리      접시에 담기      먹을 수 있는 상태
```

---

## 3. Dockerfile 분석

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 한 줄씩 설명

```dockerfile
FROM python:3.13-slim
```
> **"파이썬 3.13이 설치된 Linux 환경을 베이스로 쓸게"**
> - `FROM` = 시작점 설정 (베이스 이미지)
> - `python:3.13-slim` = 파이썬 3.13이 설치된 가벼운 Linux
> - `slim` = 불필요한 것 제거한 용량 작은 버전

---

```dockerfile
WORKDIR /app
```
> **"컨테이너 안에서 `/app` 폴더를 작업 폴더로 쓸게"**
> - `WORKDIR` = 이후 모든 명령어가 실행될 기본 경로 설정
> - 폴더가 없으면 자동 생성
> - `cd /app` 하고 거기서 계속 작업하는 것과 같음

---

```dockerfile
COPY . .
```
> **"내 컴퓨터의 현재 폴더 파일을 컨테이너의 `/app`에 복사해"**
> - 첫 번째 `.` = 내 컴퓨터의 현재 폴더 (모든 파일)
> - 두 번째 `.` = 컨테이너 안의 현재 폴더 (`/app`)
> - `main.py`, `requirements.txt` 등이 컨테이너 안으로 복사됨

---

```dockerfile
RUN pip install -r requirements.txt
```
> **"컨테이너 안에서 라이브러리 설치해"**
> - `RUN` = 이미지 빌드 중 실행할 명령어
> - `requirements.txt`에 있는 모든 라이브러리를 설치

---

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
> **"컨테이너가 시작되면 이 명령어를 실행해"**
> - `CMD` = 컨테이너 실행 시 기본으로 실행할 명령어
> - `uvicorn main:app` = FastAPI 서버 실행
> - `--host 0.0.0.0` = 외부에서 접속 가능하게 (모든 IP 허용)
> - `--port 8000` = 8000번 포트에서 실행

#### `--host 0.0.0.0` 이 왜 필요할까?

```
--host 127.0.0.1 (기본값):
  컨테이너 안에서만 접속 가능
  외부에서 접속 불가 ❌

--host 0.0.0.0:
  모든 곳에서 접속 가능
  컨테이너 밖에서도 접속 가능 ✅
```

---

### RUN vs CMD 차이

| | `RUN` | `CMD` |
|---|---|---|
| **실행 시점** | 이미지 빌드할 때 | 컨테이너 시작할 때 |
| **용도** | 설치, 설정 등 준비 작업 | 서버 실행 등 메인 작업 |
| **횟수** | 여러 번 사용 가능 | 마지막 1개만 유효 |

---

## 4. docker build - 이미지 만들기

```bash
docker build -t my-fastapi-app .
```

### 옵션 설명

| 부분 | 설명 |
|---|---|
| `docker build` | Dockerfile로 이미지를 만드는 명령어 |
| `-t my-fastapi-app` | 이미지에 이름(태그) 붙이기. `-t` = `--tag` |
| `.` | Dockerfile이 있는 경로 (현재 폴더) |

### 태그로 버전 관리

```bash
docker build -t my-fastapi-app:1.0 .   # 버전 1.0
docker build -t my-fastapi-app:2.0 .   # 버전 2.0
docker build -t my-fastapi-app:latest . # 최신 버전
```

> ⚠️ **코드를 바꾸면 꼭 `docker build`를 다시 해야 함!**
> Image는 빌드 시점의 스냅샷이라 코드가 바뀌어도 Image는 그대로!

---

## 5. docker run - 컨테이너 실행하기

```bash
docker run -p 80:8000 -d my-fastapi-app
```

### 옵션 설명

| 옵션 | 설명 |
|---|---|
| `docker run` | Image로 Container를 만들고 실행 |
| `-p 80:8000` | 포트 연결. **내 컴퓨터 80번 → 컨테이너 8000번** |
| `-d` | 백그라운드(detached) 실행. 터미널이 점유되지 않음 |
| `my-fastapi-app` | 실행할 이미지 이름 |

### `-p 포트포워딩` 이해하기

```
내 컴퓨터 포트 80  →  컨테이너 포트 8000
    ↑                       ↑
 외부에서 접속하는 포트   FastAPI가 실행 중인 포트

브라우저에서 http://localhost:80 접속
    → 컨테이너 안의 8000번 포트로 연결됨
    → FastAPI 서버 응답!
```

```bash
# 다양한 포트 설정 예시
docker run -p 80:8000 ...    # localhost:80 → 컨테이너:8000
docker run -p 3000:8000 ...  # localhost:3000 → 컨테이너:8000
docker run -p 8000:8000 ...  # localhost:8000 → 컨테이너:8000 (같은 포트)
```

### `-d` 백그라운드 실행

```bash
# -d 없이 실행
docker run -p 80:8000 my-fastapi-app
# → 터미널이 서버 로그로 가득 참, Ctrl+C 누르면 서버 종료

# -d 있으면
docker run -p 80:8000 -d my-fastapi-app
# → 터미널이 자유로움, 다른 명령어 사용 가능 ✅
```

---

## 6. docker ps - 컨테이너 목록 보기

```bash
docker ps        # 실행 중인 컨테이너만 보기
docker ps -a     # 모든 컨테이너 보기 (종료된 것 포함)
```

> ✅ `-a` = `--all` 맞아! 잘 적었어

### 출력 예시

```
CONTAINER ID   IMAGE            COMMAND                  CREATED         STATUS         PORTS                  NAMES
a1b2c3d4e5f6   my-fastapi-app   "uvicorn main:app..."   2 minutes ago   Up 2 minutes   0.0.0.0:80->8000/tcp   cool_tesla
```

| 컬럼 | 설명 |
|---|---|
| `CONTAINER ID` | 컨테이너 고유 ID |
| `IMAGE` | 어떤 이미지로 만든 컨테이너인지 |
| `STATUS` | `Up` = 실행 중, `Exited` = 종료됨 |
| `PORTS` | 포트 연결 상태 (`80->8000` = 80번이 8000번으로 연결) |
| `NAMES` | 자동으로 붙여진 컨테이너 이름 |

---

## 7. 컨테이너 안으로 들어가기

```bash
docker exec -it <컨테이너ID> bash
```

### 옵션 설명

| 옵션 | 설명 |
|---|---|
| `docker exec` | 실행 중인 컨테이너 안에서 명령어 실행 |
| `-i` | interactive, 입력을 받을 수 있게 (키보드 입력 가능) |
| `-t` | tty, 터미널처럼 보이게 (글자 색, 프롬프트 등) |
| `-it` | `-i`와 `-t`를 합친 것 (거의 항상 같이 씀) |
| `<컨테이너ID>` | 들어갈 컨테이너 ID (앞 3~4자리만 써도 됨) |
| `bash` | 컨테이너 안에서 실행할 명령어 (bash 터미널 열기) |

### 실제 사용 예시

```bash
# 컨테이너 목록 확인
docker ps
# → CONTAINER ID: a1b2c3

# 컨테이너 안으로 접속
docker exec -it a1b2 bash

# 이제 컨테이너 안의 터미널!
root@a1b2c3d4:/app#

# 파일 확인
ls        # main.py, requirements.txt 등 보임
cat main.py

# 컨테이너에서 나오기
exit      # 또는 Ctrl + D
```

> ✅ 나오는 방법 `Ctrl+D` 맞아! `exit` 명령어도 동일하게 동작해

---

## 8. 주요 Docker 명령어 모음

```bash
# 이미지 관련
docker build -t 이름 .         # 이미지 빌드
docker images                  # 이미지 목록 보기
docker rmi 이미지이름           # 이미지 삭제

# 컨테이너 관련
docker run -p 80:8000 -d 이름  # 컨테이너 실행
docker ps                      # 실행 중인 컨테이너 목록
docker ps -a                   # 전체 컨테이너 목록 (종료 포함)
docker stop 컨테이너ID          # 컨테이너 중지
docker rm 컨테이너ID            # 컨테이너 삭제
docker exec -it 컨테이너ID bash # 컨테이너 안으로 접속
docker logs 컨테이너ID          # 컨테이너 로그 보기
```

---

## 9. Docker Compose - 여러 컨테이너 관리

> ✅ "다수의 컨테이너를 손쉽게 사용" 맞아!

### 왜 필요할까?

```
실제 서비스는 컨테이너가 여러 개!

FastAPI 서버 컨테이너
    +
PostgreSQL DB 컨테이너
    +
Redis 캐시 컨테이너
    +
Nginx 웹서버 컨테이너

→ docker run 명령어를 4번 실행해야 함 ❌
→ 설정도 다 따로 해야 함 ❌
```

### Docker Compose 사용하면

```bash
docker compose up    # 전체 컨테이너 한 번에 시작 ✅
docker compose down  # 전체 컨테이너 한 번에 종료 ✅
```

### docker-compose.yml 예시

```yaml
services:
  app:            # FastAPI 서버 컨테이너
    build: .
    ports:
      - "80:8000"

  db:             # PostgreSQL DB 컨테이너
    image: postgres
    environment:
      POSTGRES_PASSWORD: password
```

---

## 10. 내가 적은 것 맞는지 확인 ✅

| 내가 적은 것 | 정확한 내용 |
|---|---|
| `docker build -t` | ✅ 맞아! `-t`는 이름(태그) 붙이기 |
| `docker ps -a` (all?) | ✅ 맞아! `-a` = `--all` 전체 목록 |
| `run -p 80:8000 -d` (background?) | ✅ 맞아! `-d` = detached = 백그라운드 실행 |
| `docker -it docker -db -1 bash` | ❌ 조금 달라! 정확한 명령어는 `docker exec -it <컨테이너ID> bash` |
| 나오는 방법 `Ctrl+D` | ✅ 맞아! `exit` 명령어도 동일 |
| 다수의 컨테이너를 손쉽게 → docker compose | ✅ 맞아! |

---

## 11. 전체 흐름 정리

```
1. 코드 작성 (main.py, requirements.txt)
        ↓
2. Dockerfile 작성 (어떻게 이미지를 만들지 레시피)
        ↓
3. docker build -t my-app .   → Image 생성
        ↓
4. docker run -p 80:8000 -d my-app  → Container 실행
        ↓
5. http://localhost:80 접속 → FastAPI 서버 응답!
        ↓
6. 코드 수정 시 → 3번부터 다시!
```

---

## 12. 용어 정리

| 용어 | 설명 |
|---|---|
| **Docker** | 코드와 실행 환경을 함께 포장해서 어디서든 실행하는 기술 |
| **Image** | 컨테이너를 만들기 위한 설계도 (읽기 전용 스냅샷) |
| **Container** | Image를 실행한 실제 프로세스 |
| **Dockerfile** | Image를 만드는 방법을 적은 파일 |
| **FROM** | 베이스 이미지 지정 |
| **WORKDIR** | 컨테이너 안의 작업 폴더 지정 |
| **COPY** | 파일을 컨테이너 안으로 복사 |
| **RUN** | 이미지 빌드 시 실행할 명령어 |
| **CMD** | 컨테이너 시작 시 실행할 명령어 |
| **`-t`** | 이미지에 이름(태그) 붙이기 |
| **`-p`** | 포트 포워딩 (내컴퓨터:컨테이너) |
| **`-d`** | 백그라운드(detached) 실행 |
| **`-it`** | 인터랙티브 터미널 모드 |
| **`docker exec`** | 실행 중인 컨테이너 안에서 명령어 실행 |
| **Docker Compose** | 여러 컨테이너를 한 번에 관리하는 도구 |
| **포트 포워딩** | 외부 포트를 컨테이너 내부 포트에 연결 |
| **0.0.0.0** | 모든 IP에서 접속 허용 |

---

> 📌 **오늘 수업 핵심 한 줄 요약**
> Docker는 코드와 실행 환경을 Container에 포장해서 어디서든 똑같이 실행하고,
> Dockerfile로 Image를 만들고, docker run으로 Container를 실행하며,
> Docker Compose로 여러 Container를 한 번에 관리!
