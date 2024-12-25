from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from app.core.helpers.pdf_generator import generate_users_pdf
from app.core.helpers.redis_cache import get_cache, set_cache, USERS_CACHE_KEY
from app.core.helpers.logging import logger
from app.db import User, get_async_session, UserRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import load_only
from app.models.users import current_active_user

router = APIRouter()

@router.get("/report/pdf", tags=["users"],  responses={ 200: {"content": {"application/pdf": {}}, "description": "PDF Report of Users",}})
async def reportPdf(db: Session = Depends(get_async_session), user: User = Depends(current_active_user)):
    try:
        logger.info("## ENDPOINT: /report/pdf")

        # Check cache
        #users_data = await get_cache(USERS_CACHE_KEY)
        users_data = False
        if users_data:
            logger.info(f"Returning users cached data: {users_data}")
        else:
            # Fetch data from database
            result = await db.execute(select(User).options(load_only(User.id, User.email, User.is_active, User.is_superuser, User.is_verified)))
            users = result.scalars().all()
            users_data = [UserRead.from_orm(user).dict() for user in users]
            for user_data in users_data:
                user_data['id'] = str(user_data['id'])  # Convert UUID to string

            logger.info(f"Getting All Users from DB: {users_data}")

            # Cache users data
            await set_cache(USERS_CACHE_KEY, users_data)

        pdf_buffer = generate_users_pdf(users_data)

        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": "inline; filename=employers.pdf"})

    except Exception as e:
        logger.error(f"Error exporting users: {e}")
        return {"success": False, "error": "Failed to export users to pdf"}