from pydantic import BaseModel

class SalleBase(BaseModel):
    nom: str
    capacite: int | None = None

class SalleCreate(SalleBase):
    pass

class SalleUpdate(SalleBase):
    nom: str | None = None

class SalleOut(SalleBase):
    id: int
    class Config:
        from_attributes = True