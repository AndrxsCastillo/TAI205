# 1. Importaciones
from fastapi import FastAPI
from app.routers import usuarios, varios

# 2. Inicialización de APP
app= FastAPI(
    title='Mi Primer API',
    description="Andrés Castillo",
    version='1.0.0'
)

app.include_router(usuarios.routerU)
app.include_router(varios.routerV)
