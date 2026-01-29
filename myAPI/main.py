# 1. Importaciones
from fastapi import FastAPI


# 2. Inicialización de APP
app= FastAPI()


#3. Endpoints
@app.get("/") # Endpoint de inicio
async def holaMundo():
    return  {"mensaje":"Hola mundo FASTAPI"}

@app.get("/bienvenida")
async def bien():
    return {"mensaje":"Bienvenidos"}

