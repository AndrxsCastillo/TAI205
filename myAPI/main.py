# 1. Importaciones
from fastapi import FastAPI
from typing import Optional
import asyncio


# 2. Inicialización de APP
app= FastAPI(title='Mi Primer API',
             description="Andrés Castillo",
             version='1.0.0'
             )

# BD ficticia
usuarios=[
    {"ïd":"1","nombre":"Andrés","edad":"21"},
    {"ïd":"2","nombre":"Rafael","edad":"22"},
    {"ïd":"3","nombre":"Leonardo","edad":"20"},
]


#3. Endpoints
@app.get("/", tags=['Inicio']) # Endpoint de inicio
async def holaMundo():
    return  {"mensaje":"Hola mundo FASTAPI"}

@app.get("/bienvenida", tags=['Inicio'])
async def bien():
    return {"mensaje":"Bienvenidos"}

@app.get("/v1/promedio", tags=['Calificaciones']) # Creación de nuevo endpoint
async def promedio():
    await asyncio.sleep(3) # Petición a otra API, consulta a BD, etc
    return {"Calificacion":"9",
            "Estatus":"200"
            }

@app.get("/v1/usuario/{id}", tags=['Parámetros']) # Colocar {} después de la ruta hace el parámetro obligatorio
async def consultaUno(id:int):
    await asyncio.sleep(3)
    return {"Resultado":"Usuario encontrado",
            "Estatus":"200"
            }


@app.get("/v1/usuarios_op/", tags=['Parámetro Opcional']) # Endpoint con parámetro opcional
async def consultaOp(id:Optional[int]=None):
    await asyncio.sleep(2)
    if id is not None:
        for usuario in usuarios:
            if usuario ["id"] == id:
                return {"Usuario encontrado":id, "Datos":usuario}
        return{"Mensaje":"Usuario no encontrado"}
    else:
        return {"Aviso":"No se proporcionó ID"}
