from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.helpers.pdf_generator import generate_users_pdf
from app.core.helpers.logging import logger
from app.core.helpers.cache import cache_data, CACHE_KEY_USERS_GET_ALL

from app.db import User, get_async_session, UserRead
from app.models.users import current_active_user

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import load_only

router = APIRouter()


@router.get("/report/pdf", tags=["users"],  responses={ 200: {"content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}}, "description": "PDF Report of Users",}})
async def reportPdf(db: Session = Depends(get_async_session), user: User = Depends(current_active_user)):
    try:
        logger.info("## ENDPOINT: /report/pdf")

        users_data = await get_all_users(db)

        pdf_buffer = generate_users_pdf(users_data)

        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=users.pdf"})

    except Exception as e:
        logger.error(f"Error exporting users: {e}")
        return {"success": False, "error": "Failed to export users to pdf"}

@cache_data(key=CACHE_KEY_USERS_GET_ALL, expire=None)
async def get_all_users(db: Session):
    try:
        result = await db.execute(
            select(User).options(
                load_only(
                    User.id, User.email, User.is_active, User.is_superuser, User.is_verified
                )
            )
        )
        users = result.scalars().all()
        users_data = [UserRead.from_orm(user).dict() for user in users]
        for user_data in users_data:
            user_data['id'] = str(user_data['id'])  # Convert UUID to string

        return users_data
    except Exception as e:
        logger.error(f"Error fetching users from database: {e}")
        return []