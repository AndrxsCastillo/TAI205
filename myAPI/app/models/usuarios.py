# Modelo de validación Pydantic, creación del modelo
from pydantic import BaseModel, Field

class crear_usuario(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50, example="Juanita") # Validaciones personalizadas
    edad: int = Field(..., ge=1, le=123, description="Edad válida entre 1 y 123")