# Importaciones
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
import asyncio
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone


# Configuración JWT

# Clave secreta usada para firmar los tokens JWT
SECRET_KEY = "clave_super_secreta_para_firmar_tokens_jwt_2024"

# Algoritmo de firmado
ALGORITHM = "HS256"

# Tiempo máximo de vida del token de 30 minutos
MAX_TOKEN_MINUTOS = 30


# CONFIGURACIÓN DE PASSLIB
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Consiguración OAUTH2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/token")


# Base de datos ficticia de usuarios con contraseñas hasheadas
usuarios_auth = {
    "andrescastillo": {
        "username": "andrescastillo",
        "nombre_completo": "Andrés Castillo",
        "hashed_password": pwd_context.hash("123456"),
        "activo": True,
    },
    "rafael": {
        "username": "rafael",
        "nombre_completo": "Rafael López",
        "hashed_password": pwd_context.hash("abcdef"),
        "activo": True,
    },
}

# Base de datos ficticia de usuarios del CRUD
usuarios = [
    {"id": 1, "nombre": "Andrés", "edad": "21"},
    {"id": 2, "nombre": "Rafael", "edad": "22"},
    {"id": 3, "nombre": "Leonardo", "edad": "20"},
]


# Modelos Pydantic
# Modelo para crear usuarios del CRUD
class CrearUsuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=3, max_length=50, example="Juanita")
    edad: int = Field(..., ge=1, le=123, description="Edad válida entre 1 y 123")

# Modelo que representa al usuario autenticado (lo que guardamos dentro del token)
class TokenData(BaseModel):
    username: Optional[str] = None

# Modelo de la respuesta cuando se genera un token exitosamente
class Token(BaseModel):
    access_token: str          # El token JWT en sí
    token_type: str            # Siempre "bearer" según el estándar OAuth2

# Modelo del usuario en la app (sin contraseña)
class Usuario(BaseModel):
    username: str
    nombre_completo: Optional[str] = None
    activo: Optional[bool] = None


# Funciones de utilidad JWT
def verificar_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def autenticar_usuario(username: str, password: str):
    usuario = usuarios_auth.get(username)
    if not usuario:
        return False
    if not verificar_password(password, usuario["hashed_password"]):
        return False
    return usuario

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    # "exp" es un claim estándar de JWT que indica cuándo expira el token
    to_encode.update({"exp": expire})

    # jwt.encode() serializa y firma el diccionario
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},   # Estándar OAuth2
    )

    try:
        # jwt.decode() verifica la firma Y la expiración automáticamente.
        # Si el token expiró, lanza un JWTError con mensaje "Signature has expired."
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")   # "sub" = subject (quién es el usuario)
        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)

    except JWTError:
        # Captura tokens malformados, firmados con otra clave O expirados
        raise credentials_exception

    # Verificar que el usuario todavía exista en la "base de datos"
    usuario = usuarios_auth.get(token_data.username)
    if usuario is None:
        raise credentials_exception

    return usuario


# Inicialización de la app
app = FastAPI(
    title="Mi API con OAuth2 + JWT",
    description="Andrés Castillo",
    version="1.0.0",
)


# Endpoints
@app.get("/", tags=["Inicio"])
async def hola_mundo():
    return {"mensaje": "Hola mundo FastAPI"}

@app.get("/bienvenida", tags=["Inicio"])
async def bienvenida():
    return {"mensaje": "Bienvenidos"}

# Endpoint de autenticación — Genera el token JWT
@app.post("/v1/token", response_model=Token, tags=["Autenticación"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = autenticar_usuario(form_data.username, form_data.password)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear el token con tiempo de expiración máximo de 30 minutos
    tiempo_expiracion = timedelta(minutes=MAX_TOKEN_MINUTOS)
    access_token = crear_token_acceso(
        data={"sub": usuario["username"]},   # "sub" identifica al usuario
        expires_delta=tiempo_expiracion,
    )

    return {"access_token": access_token, "token_type": "bearer"}

# Ver usuario autenticado actual
@app.get("/v1/usuarios/yo", tags=["Autenticación"])
async def leer_usuario_actual(usuario_actual=Depends(obtener_usuario_actual)):
    return {
        "username": usuario_actual["username"],
        "nombre_completo": usuario_actual["nombre_completo"],
        "activo": usuario_actual["activo"],
    }

@app.get("/v1/promedio", tags=["Calificaciones"])
async def promedio():
    await asyncio.sleep(3)
    return {"Calificacion": "9", "Estatus": "200"}

@app.get("/v1/usuarioO/{id}", tags=["Parámetros"])
async def consulta_uno(id: int):
    await asyncio.sleep(3)
    return {"Resultado": "Usuario encontrado", "Estatus": "200"}

@app.get("/v1/usuarios_op/", tags=["Parámetro Opcional"])
async def consulta_op(id: Optional[int] = None):
    await asyncio.sleep(2)
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return {"Usuario encontrado": id, "Datos": usuario}
        return {"Mensaje": "Usuario no encontrado"}
    else:
        return {"Aviso": "No se proporcionó ID"}

# CRUD HTTP
@app.get("/v1/usuarios/", tags=["CRUD HTTP"])
async def consulta_todos():
    return {
        "status": "200",
        "total": len(usuarios),
        "data": usuarios,
    }

@app.post("/v1/usuarios/", tags=["CRUD HTTP"], status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: CrearUsuario):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(status_code=400, detail="El ID ya existe")
    usuarios.append(usuario.dict())
    return {
        "mensaje": "Usuario agregado correctamente",
        "status": "201",
        "usuario": usuario,
    }

# Endpoint PUT protegido con JWT
@app.put("/v1/usuarios/{id}", tags=["CRUD HTTP"])
async def actualizar_usuario(
    id: int,
    usuario_actualizado: dict,
    usuario_actual=Depends(obtener_usuario_actual), # Requiere token válido
):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usuarios[index] = usuario_actualizado
            return {
                "mensaje": f"Usuario actualizado por: {usuario_actual['username']}",
                "datos": usuarios[index],
            }

    raise HTTPException(status_code=404, detail="Usuario no encontrado")

# Endpoint DELETE protegido con JWT
@app.delete("/v1/usuarios/{id}", tags=["CRUD HTTP"])
async def eliminar_usuario(
    id: int,
    usuario_actual=Depends(obtener_usuario_actual), # Requiere token válido
):
    for usr in usuarios:
        if usr["id"] == id:
            usuarios.remove(usr)
            return {
                "mensaje": f"Usuario {id} eliminado por: {usuario_actual['username']}",
            }

    raise HTTPException(status_code=404, detail="No se encontró el usuario para eliminar")
