from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, BackgroundTasks
import asyncio

# Глобальна черга завдань
task_queue = asyncio.Queue()


# Асинхронна функція для виконання конкретного завдання
async def task_send_word(word: str):
    print(f"start {word}")  # Початок виконання завдання
    for i in range(10):  # Емуляція тривалого процесу (10 ітерацій)
        print(f"{word}, {i}")  # Логування поточного стану
        await asyncio.sleep(1)  # Пауза між ітераціями
    print(f"stop {word}")  # Завершення завдання


# Функція для обробки завдань у черзі
async def process_task_queue():
    while True:
        task = await task_queue.get()  # Отримання завдання з черги
        if task is None:  # Умовний сигнал завершення
            break
        await task  # Виконання отриманого завдання
        task_queue.task_done()  # Позначення завдання як виконаного


# Менеджер контексту для управління життєвим циклом додатку
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    print("Process start")  # Логування початку життєвого циклу додатку
    worker = asyncio.create_task(process_task_queue())  # Запуск обробника черги в окремому завданні

    yield  # Пауза, поки додаток працює

    print("End app, stop process")  # Логування завершення роботи додатку
    await task_queue.put(None)  # Додавання сигналу завершення в чергу
    await worker  # Очікування завершення обробника черги

    print("all workers done")  # Логування після завершення всіх задач


# Ініціалізація FastAPI-додатку з користувацьким життєвим циклом
app = FastAPI(lifespan=app_lifespan, docs_url="/")  # docs_url змінено для демонстрації


# Ендпоінт для додавання нового завдання до черги
@app.post("/add-task/")
async def add_task(background_tasks: BackgroundTasks, word: str = "task"):
    print(f"---task post: {word}")  # Логування отриманого слова
    # Додавання завдання до черги через BackgroundTasks
    background_tasks.add_task(task_queue.put, task_send_word(word))
    return {"message": f"Завдання {word} додано до черги"}  # Відповідь клієнту


# Ендпоінт для привітання
@app.get("/")
async def read_root():
    return {"message": "Вітаємо у FastAPI з фоновими завданнями та чергою"}


# Запуск додатку за допомогою uvicorn
if __name__ == "__main__":
    uvicorn.run(f"{__name__}:app", workers=6)  # Використання 6 воркерів для обробки запитів