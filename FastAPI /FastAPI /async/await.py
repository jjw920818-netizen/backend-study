# await 키워드 = I/O 대기가 발생한느 순간, 실행권을 양보하는 키워드
import asyncio
import time


# 동기식 살향사건 -> 6초
def task_a():
    print("A 시작")
    time.sleep(3)
    print("A 끝")

def task_b():
    print("B 시작")
    time.sleep(3)
    print("B 끝")

print("=== 동기 실행 ===")
sync_start = time.time()
task_a()
task_b()
sync_end = time.time()
print(f"{sync_end - sync_start:.2f}초")

# 비동기식
async def coro_a():
    print("A 시작") # 1
    await asyncio.sleep(3) # 2 -> 양보
    print("A 끝") # 5 

async def coro_b():
    print("B 시작") # 3
    await asyncio.sleep(3) # 4 -> 양보
    print("B 끝") # 6

async def main():
    a = coro_a()
    b = coro_b()
    await asyncio.gather(a, b) 

print("=== 비동기 실행 ===")
async_start = time.time()
asyncio.run(main())
async_end = time.time()
print(f"{async_end - async_start:.2f}초")

# [ 정 리 ]
# 1. await 키워드를 통해서 코루틴 함수 안에서 실행권을 양보할 수 있다.
# 2. await 키워드는 대기가 발행하는 코드(sleep, I/O 대기) 앞에 붙인다.
# 3. 대기시간 동안 다른 코루틴이 실행되어, 전체 프로그램 대기시간을 줄일 수 있다.

# 3초식 대기하는 ㅎ마수 3개를 실행한다면,
#   동기 방식-> 9초
#   비동기방식 -> 3초

# 비동기 방식의 단점
# 1. 코루틴이 정확히 어떤 순서로 실행될지 보장할 수 없음
# 2. 실행 잘못 시키면, 오히려 더 비효율적 동작
# -> 비동기 프로그래밍이 어떤 실행 흐름으로 동작하는지 이해하고 사용해야 함

# 🌟 await 를 쓴느 두 가지 조건 🌟
# 1. 비동기 함수(코루틴) 안에서만 사용 가능 -> 반드시 async def 함수 안에서만
# 2. 기다려야 하는 작업일 때 (awaitable일 때)
#                     awaitable 인지 판단하는 방법 async def 정의된 함수인가?, 비동기 라이브러리에서 온 함수인가? I/O 대기 시간이 발생하는 작업인다?