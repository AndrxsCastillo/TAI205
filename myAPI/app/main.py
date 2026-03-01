# 1. Importaciones
from fastapi import FastAPI, status, HTTPException
from typing import Optional
import asyncio
from typing import Optional
from pydantic import BaseModel, Field


# 2. Inicialización de APP
app= FastAPI(title='Mi Primer API',
             description="Andrés Castillo",
             version='1.0.0'
             )

# BD ficticia
usuarios=[
    {"id":"1","nombre":"Andrés","edad":"21"},
    {"id":"2","nombre":"Rafael","edad":"22"},
    {"id":"3","nombre":"Leonardo","edad":"20"},
]


# Modelo de validación Pydantic, creación del modelo
class crear_usuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario") # Validaciones personalizadas
    nombre: str = Field(..., min_length=3, max_length=50, example="Juanita")
    edad: int = Field(..., ge=1, le=123, description="Edad válida entre 1 y 123")


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

@app.get("/v1/usuarioO/{id}", tags=['Parámetros']) # Colocar {} después de la ruta hace el parámetro obligatorio
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
    

@app.get("/v1/usuarios/", tags=['CRUD HTTP']) # Endpoint GET
async def consultaT():
    return{
        "status":"200",
        "total": len(usuarios),
        "data": usuarios
    }


@app.post("/v1/usuarios/", tags=['CRUD HTTP'], status_code=status.HTTP_201_CREATED) # Endpoint POST
async def crearUsuario(usuario:crear_usuario): # Uso del modelo
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400,
                detail="El ID ya existe"
            )
    usuarios.append(usuario)
    return{
        "mensaje":"Usuario agregado correctamente",
        "status":"200",
        "usuario":usuario
    }


@app.put("/v1/usuarios/{id}", tags=['CRUD HTTP']) # Enpoint PUT
async def actualizarUsuario(id: str, usuario_actualizado: dict):
    # Buscamos el usuario por su ID
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            # Reemplazamos los datos del usuario en esa posición
            usuarios[index] = usuario_actualizado
            return {
                "mensaje":"Usuario actualizado correctamente",
                "datos":usuarios[index]
            }
    
    # En caso de no encontrar al usuario, lanzamos un error
    raise HTTPException(
        status_code=400,
        detail="Usuario no encontrado"
    )


@app.delete("/v1/usuarios/{id}", tags=['CRUD HTTP']) # Endpoint DELETE
async def eliminarUsuario(id: str):
    # Buscamos el usuario en la lista
    for usr in usuarios:
        if usr["id"] == id:
            usuarios.remove(usr)
            return {
                "mensaje": "Usuario eliminado exitosamente",
                "id_eliminado": id
            }
    
    # Si no lo encuentra manda error
    raise HTTPException(
        status_code=400,
        detail="No se encontró el usuario para eliminar"
    )
