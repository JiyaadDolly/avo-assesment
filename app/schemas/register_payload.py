from pydantic import BaseModel

class RegisterPayload(BaseModel):
    first_name: str
    last_name: str
    email: str