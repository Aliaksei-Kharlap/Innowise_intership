from pydantic import BaseModel


class HumanBase(BaseModel):
    human_name: str
    birth_year: int

class HumanCreate(HumanBase):
    pass


class Human(HumanBase):
    id: int
    country_id: int

    class Config:
        orm_mode = True

class CountryBase(BaseModel):
    country_name: str

class CountryCreate(CountryBase):
    pass

class Country(CountryBase):
    id: int
    people: list[Human] = []
    class Config:
        orm_mode = True