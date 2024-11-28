from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, BackgroundTasks
import asyncio

task_queue = asyncio.Queue()


async def task_send_word(word: str):
    print(f"start {word}")
    for i in range(10):
        print(f"{word}, {i}")
        await asyncio.sleep(1)
    print(f"stop {word}")


async def process_task_queue():
    while True:
        task = await task_queue.get()
        if task is None:
            break
        await task
        task_queue.task_done()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # before start app
    print("Process start")
    worker = asyncio.create_task(process_task_queue())

    yield

    print("End app, stop process")
    await task_queue.put(None)
    await worker

    print("all workers done")
    # after stop app


app = FastAPI(lifespan=app_lifespan, docs_url="/")


@app.post("/add-task/")
async def add_task(background_tasks: BackgroundTasks, word: str = "task"):
    print(f"---task post: {word}")
    background_tasks.add_task(task_queue.put, task_send_word(word))
    return {"message": f"Завдання {word} додано до черги"}


@app.get("/")
async def read_root():
    return {"message": "Вітаємо у FastAPI з фоновими завданнями та чергою"}


if __name__ == "__main__":
    uvicorn.run(f"{__name__}:app", workers=6)
