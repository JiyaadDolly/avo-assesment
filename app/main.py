
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.db import create_db_and_tables
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.models.users import auth_backend, fastapi_users
from api.user.v1.users import router as users_router

def get_application():
    _app = FastAPI()

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app

app = get_application()

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/api/v1/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/api/v1/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/api/v1/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/api/v1/auth", tags=["auth"],)
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/api/v1/users", tags=["users"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])