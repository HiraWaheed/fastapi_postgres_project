from pydantic import BaseModel


class UserCreate(BaseModel):
    """
    Schema for creating a user, with a password included.
    """

    username: str
    password: str


class UserCreateResponse(BaseModel):
    """
    Schema for displaying user details without the password.
    """

    username: str


class UserToken(BaseModel):
    """Schema for returning the JWT token and its type."""

    access_token: str
    token_type: str

    class Config:
        orm_mode = True
