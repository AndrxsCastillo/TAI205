from fastapi import status, HTTPException, Depends

from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets


# Seguridad HTTP BASIC
seguridad = HTTPBasic()

def verificar_peticion(credenciales:HTTPBasicCredentials=Depends(seguridad)):
    userAuth = secrets.compare_digest(credenciales.username, "andrescastillo")
    passAuth = secrets.compare_digest(credenciales.password, "123456")

    if not(userAuth and passAuth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            deefault="Credenciales no autorizadas"
        )