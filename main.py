import uvicorn
from fastapi import FastAPI, BackgroundTasks
import asyncio
import logging
from settings import logger


app = FastAPI(docs_url="/")


async def send_email(email: str):
    await asyncio.sleep(7)
    print(f"Email sent to {email}")


@app.post("/send-email/")
async def send_email_endpoint(background_tasks: BackgroundTasks, email: str):
    background_tasks.add_task(send_email, email)
    return {"message": "Email sending in the background"}


@app.get("/hello")
async def read_root(background_tasks: BackgroundTasks):
    background_tasks.add_task(logger.info, msg="INFO_Welcome to FastAPI with async tasks")
    background_tasks.add_task(logger.error, msg="ERROR Welcome to FastAPI with async tasks")
    return {"message": "Welcome to FastAPI with async tasks"}


@app.get("/default_log_levels")
async def log_levels():
    logging.debug("is debug log")
    logging.info("is INFO log")
    logging.warning("is INFO log")
    logging.error("is Error log")
    logging.critical("is critical log")

    return {"message": "Welcome to FastAPI with async tasks"}


@app.get("/my_log_in_file")
async def log_in_file():
    logger.debug("is debug log")
    logger.info("is INFO log")
    logger.warning("is INFO log")
    logger.error("is Error log")
    logger.critical("is critical log")

    return {"message": "log is created"}

if __name__ == "__main__":
    uvicorn.run(f"{__name__}:app", reload=True)
