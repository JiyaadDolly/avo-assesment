from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from random import randrange
from app.models.employer import Employer
from app.database import get_db
from app.pdf_generator import generate_employers_pdf
from app.redis_cache import get_cache, set_cache, invalidate_cache, EMPLOYERS_CACHE_KEY
from app.logging import logger
from app.schemas.register_payload import RegisterPayload

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

@app.get("/ping")
async def ping():

    logger.info("## ENDPOINT: /ping")
    return {"Pong"}

@app.get("/employers")
async def getAll(db: Session = Depends(get_db)):

    try:
        logger.info(f"## ENDPOINT: /employers")

        # Check cache
        employees = await get_cache(EMPLOYERS_CACHE_KEY)
        if employees:
            logger.info("Returning employers cached data")
            return {"success": True, "data": employees}

        # Fetch data from database
        employees = db.query(Employer).all()
        employees_data = [emp.as_dict() for emp in employees]
        logger.info(f"Getting All Employees from DB: {employees_data}")

        # Cache employer data
        await set_cache(EMPLOYERS_CACHE_KEY, employees_data)

        return {"success" : True, "data": employees_data}

    except Exception as e:

        logger.error(f"Error fetching employees: {e}")
        return { "success" : False, "error": "Failed to fetch employees" }

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterPayload, db: Session = Depends(get_db)):

    try:
        logger.info(f"## ENDPOINT: /register | {payload}")

        employer = Employer(first_name=payload.first_name, last_name=payload.last_name, email=payload.email)
        db.add(employer)
        db.commit()
        db.refresh(employer)
        logger.info(f"Employer added: {employer.as_dict()}")

        # Invalidate cache
        logger.info("Invalidating employer cache")
        await invalidate_cache(EMPLOYERS_CACHE_KEY)

        return { "success" : True, "data": employer.as_dict() }

    except Exception as e:

        logger.error(f"Error adding employer: {e}")
        return {"success" : False, "error": "Failed to add employer"}

@app.get("/employers/report/pdf")
async def export_employers(db: Session = Depends(get_db)):

    try:
        logger.info("## ENDPOINT: /export-employers")

        # Call getAll to get the data
        response = await getAll(db)
        if not response["success"]:
            return response

        employers = response["data"]

        pdf_buffer = generate_employers_pdf(employers)

        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": "inline; filename=employers.pdf"})

    except Exception as e:
        logger.error(f"Error exporting employers: {e}")
        return {"success": False, "error": "Failed to export employers"}