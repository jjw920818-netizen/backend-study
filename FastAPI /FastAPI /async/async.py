# 비동기 프로그래밍
# 동기 프로그랭에서 발생한느 대기 시간동안 다른 작업을 할 수 있게 하는 프로그래밍 방식

# 동기식 -> 물 끓이는 동안, 그자리에서 계속 기다리는 것
# 비동기식 -> 물 끓이는 동안, 반찬, 카톡, 물 등등 준비 )

# asyncio 라이브러리(표준 라이브러리)
# Async + IO -> I/O(Input/Output)작업에서 발색하는 대기시간 동안 비동기
import asyncio

# 비동기 함수 (= 코루틴 함수)
async def hello():
    print("hello")
# 비동기 함수를 호출()하면, 즉시 실행되지 않고, 코루틴(coroutine) 생성
# 코루틴 = Co + routine -> 여러개 같이 동작하는 함수 혼자 독점하지 않고, 서로 양보하면서 실행되는 함수

# coroutine = hello() 
# print(coroutine)

# 비동기 함수를 실행
coroutine = hello() 
asyncio.run(coroutine)


# [ 정 리 ]
# 1. async def로 정의하면, 코루틴 함수를 생성한다.
# 2. 코루틴 함수를 호출()하면, 즉시 실행되지 않고 코루틴을 생성한다.
# 3. 코루틴은 동시에 같이 실행되기 위한 함수들이다.


