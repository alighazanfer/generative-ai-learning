from pydantic import BaseModel


class Customer(BaseModel):
    name: str
    phone: str
    city: str


class Pet(BaseModel):
    breed: str
    weight: str
    age: int
    coat: str
    notes: str


class QualifyLead(BaseModel):
    customer: Customer
    pet: Pet


class GlobalState(BaseModel):
    query: str
    qualify_lead: QualifyLead
