import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from database import initialize_database, save, UserManager, ChallengeManager, PostManager

storage, db, connection, root = initialize_database()

user_manager = UserManager(root)
challenge_manager = ChallengeManager(root)
post_manager = PostManager(root)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    
    # on shutdown
    save()
    connection.close()
    db.close()
    storage.close()
    
# initial config
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

# include routers
from routes import main as main_router
from auth import auth as auth_router
app.include_router(main_router)
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(app, reload=True)