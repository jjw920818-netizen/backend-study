import asyncio
import time

async def good_task():
    print("착한 Task 시작")
    await asyncio.sleep(5)
    print("착한 Task 종료")

async def bad_task():
    print("나쁜 Task 시작")
    time.sleep(5)
    print("나쁜 Task 종료")

async def main():
    await asyncio.gather(
        good_task(),
        good_task(),
        good_task(),
        good_task(),
        good_task(), 
        bad_task(),
        )

asyncio.run(main())