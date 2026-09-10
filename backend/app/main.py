from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router


app = FastAPI(title="TeamDeck API")



        
app.include_router(auth_router)
app.include_router(users_router)