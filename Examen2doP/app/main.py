from fastapi import FastAPI, status, HTTPException, Depends
from typing import Optional
import asyncio
from pydantic import BaseModel, Field
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

# Inicialización de la API
app= FastAPI(
    title='API Sistema de Reservas Hospedaje',
    description="Examen 2do Parcial",
    version='1.0.0'
)

# Base de datos ficticia
reservas = [
    {"id":1,"nombreHuesped":"Andrés", "fechaEntrada":"2025-06-01", "fechaSalida":"2025-06-05", "tipoHabitacion": "Doble", "diasEstancia": 5},
    {"id":2,"nombreHuesped":"Rafael", "fechaEntrada":"2025-06-02", "fechaSalida":"2025-06-06", "tipoHabitacion": "Sencilla", "diasEstancia": 5},
    {"id":3,"nombreHuesped":"Leonardo", "fechaEntrada":"2025-06-03", "fechaSalida":"2025-06-07", "tipoHabitacion": "Suite", "diasEstancia": 5}
]

# Modelo de validación Pydantic
class crear_reserva(BaseModel):
    id: int = Field(..., ge=1, description="Identificador de reserva")
    nombreHuesped: str = Field(..., min_length=5, example="Juanita")
    fechaEntrada: str = Field(..., description="Fecha de entrada en formato YYYY-MM-DD")
    fechaSalida: str = Field(..., gt=fechaEntrada, description="Fecha de salida mayor que fecha de entrada")
    tipoHabitacion: str = Field(...,["Sencilla", "Doble", "Suite"])
    diasEstancia: int = Field(..., le=7, description="La estancia no puede ser mayor a 7 días")

# Seguridad HTTP BASIC
seguridad = HTTPBasic()

def verificar_peticion(credenciales:HTTPBasicCredentials=Depends(seguridad)):
    userAuth = secrets.compare_digest(credenciales.username, "hotel")
    passAuth = secrets.compare_digest(credenciales.password, "r2026")

    if not(userAuth and passAuth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            deefault="Credenciales no autorizadas"
        )
    
# Endpoints
@app.get("/bienvenida", tags=['Inicio'])
async def bien():
    return {"mensaje":"Bienvenidos"}

# Crear reservas
@app.post("/v1/reservas/", tags=['RESERVAS'], status_code=status.HTTP_201_CREATED)
async def crearReserva(reserva:crear_reserva, userAuth:str=Depends(verificar_peticion)): # Uso del modelo
    for usr in reserva:
        if usr["id"] == reserva.id:
            raise HTTPException(
                status_code=400,
                detail="El ID ya existe"
            )
    reservas.append(reserva)
    return{
        "mensaje": f"Reserva agregada correctamente por {userAuth}",
        "status": "200",
        "usuario": reserva
    }

# Listar reservas
@app.get("/v1/reservas/", tags=['RESERVAS'])
async def consultarReservas():
    return{
        "status":"200",
        "total": len(reservas),
        "data": reservas
    }

# Consultar por ID
@app.get("/v1/reservas/{id}", tags=['RESERVAS'])
async def consultarPorId():
    for reserva in reservas:
        if reserva["id"] == id:
            return {
                "status":"200",
                "data": reserva
            }
    raise HTTPException(
        status_code=404,
        detail="Reserva no encontrada"
    )

# Confirmar reserva
@app.post("/v1/reservas/{id}/confirmar", tags=['RESERVAS'])
async def confirmarReserva(id: int, userAuth:str=Depends(verificar_peticion)):
    for reserva in reservas:
        if reserva["id"] == id:
            return {
                "mensaje": f"Reserva confirmada por {userAuth}",
                "status": 200,
                "data": reserva
            }
    raise HTTPException(
        status_code=404,
        detail="Reserva no encontrada para confirmar"
    )

# Cancelar reserva
@app.delete("/v1/reservas/{id}", tags=['CRUD HTTP'])
async def cancelarReserva(id: int, userAuth:str=Depends(verificar_peticion)):
    for usr in reservas:
        if usr["id"] == id:
            reservas.remove(usr)
            return {
                "mensaje": f"Reserva cancelada por {userAuth}"
            }
    raise HTTPException(
        status_code=404,
        detail="No se encontró la reserva para eliminar"
    )

