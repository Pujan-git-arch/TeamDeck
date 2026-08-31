from fastapi import FastAPI

app = FastAPI(title="TeamDeck API")


@app.get("/")
def root():
    return {"message": "TeamDeck API is running"}