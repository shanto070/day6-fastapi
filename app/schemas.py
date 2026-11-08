from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    age: int = Field(ge=1, le=120)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    age: int | None = Field(default=None, ge=1, le=120)
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)