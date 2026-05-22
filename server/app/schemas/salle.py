from pydantic import BaseModel
from typing import Optional


class SalleBase(BaseModel):
    code: str
    designation: Optional[str] = None
    capacite: Optional[int] = None
    batiment: Optional[str] = None


class SalleCreate(SalleBase):
    pass


class SalleUpdate(BaseModel):
    code: Optional[str] = None
    designation: Optional[str] = None
    capacite: Optional[int] = None
    batiment: Optional[str] = None


class SalleOut(SalleBase):
    id: int

    class Config:
        from_attributes = True