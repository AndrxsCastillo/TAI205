# 1. Importaciones
from fastapi import FastAPI
from app.routers import usuarios, varios
from app.data.db import engine
from app.data import usuario

# Instrucción para que en caso de que no exista la tabla, la cree
usuario.Base.metadata.create_all(bind=engine)

# 2. Inicialización de APP
app= FastAPI(
    title='Mi Primer API',
    description="Andrés Castillo",
    version='1.0.0'
)

app.include_router(usuarios.routerU)
app.include_router(varios.routerV)
