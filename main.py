from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from src.routers import profile, user_requests
from config import settings

Base.metadata.create_all(engine)

app = FastAPI(root_path="/v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f'https//:{settings.DOMAIN_NAME}'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


SECRET_KEY = settings.APP_SECRET_KEY

app.include_router(profile.router, tags=["profile-controller"])
app.include_router(user_requests.router, tags=["user-requests-controller"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
