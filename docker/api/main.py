import json
import uuid

from redis import asyncio as aredis
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse

redis_client = aredis.from_url("redis://redis:6379", decode_responses=True) #✔️responseS 

# import time
# import asyncio

# async def corol():
#     await time.sleep(3)  # time.sleep은 동기라 await 불가

# 답변 생성을 요청하면, 대기 발생
# 대기하는 동안, 다른 일(HTTP 요청) 처리

# llm = Llama()

app = FastAPI()

# [ 쿼리 파라미터(QueryParameter) ]
# GET google.com/search?q=pythom -> 새로운 데이터를 만들어내거나, 데이터 변경 X
# POST -> 새로운 데이터를 생성

# 1) 클라이언트에서 질문(question)을 전달한다.
@app.post("/chats")
async def chat_handler(
    # RequestBody
    question: str = Body(..., embed=True),

    #Query Parameter
    # question: str = Query(...),

    # Path
    # question: str = Path(...),
):
    # 2) 결과 채널을 구독
    job_id = str(uuid.uuid4()) # 작업을 식별할 수 있는 랜덤 식별자 발급
    channel = f"result:{job_id}"

    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    # 3) 답변 생성 작업 Enqueue 
    job = {"id": job_id,"question": question}
    await redis_client.lpush("inference_queue",json.dumps(job))

    # 4) 답볍 생성 결과를 돌려받기
    async def event_generator():
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                if data == "[DONE]":
                    break
                yield data

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


# 🌟 
# 1) Path
# 2) Query
# 3) Request Body
#   3)-1 Base 모델에서 상속받은 class 정의  xxx : UserSignUpRequest = Body
#   3)-2

