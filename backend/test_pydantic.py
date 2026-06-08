
from pydantic import BaseModel

class TCreate(BaseModel):
    contrasena: str

data = TCreate(contrasena='admin123')
data.contrasena = 'hashed_123'
print(data.model_dump())

