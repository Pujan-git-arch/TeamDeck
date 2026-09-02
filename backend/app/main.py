from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine

app = FastAPI(title="TeamDeck API")


@app.get("/")
def root():
    return {"message": "TeamDeck API is running"}

@app.get("/db-test")
def db_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {
            "database": result.scalar()
        }