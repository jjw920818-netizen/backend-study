# Llama 추론 프로그램 -> CPU 작업
# 답변생성하기
import json
import redis
from llama_cpp import Llama

# redis = (비유) 엄청 빠른 초소형 데이터베이스(key:value)
redis_client = redis.from_url("redis://redis:6379", decode_responses=True)

# 비동기 프로그래밍을 적용해야 할까요? NO
# I/O 작업에 효과적 -> "대기시간에 다른거 하자"

llm = Llama(
    model_path ="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
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
      messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
      ],
      max_tokens=256,
      temperature=0.7,
      stream=True,
   )
   return response

def run():
   while True:
    # [1] Job을 deque
    _, job_data = redis_client.brpop("inference_queue")
    job : dict = json.loads(job_data)

    # [2] 추론
    stream = create_response(question = job["question"])

    # [3] 결과를 API 서버로 반환
    channel = f"result:{job['id']}"
    for chunk in stream:
       token = chunk["choices"][0]["delta"].get("content")
       if token:
          redis_client.publish(channel, token)     
    redis_client.publish(channel, "[DONE]")

# python main.py로 실행되었을 때만, runs()을 호출
if __name__ == "__main__":
    run()

