from pydantic import BaseModel


class CandidateBase(BaseModel):
    """
    Base schema for common user attributes.
    """

    first_name: str
    last_name: str
    experience: int

    class Config:
        orm_mode = True
        from_attributes = True


class CandidateCreateResponse(BaseModel):
    """
    Base schema for returning candidate info
    """

    id: int

    class Config:
        orm_mode = True
