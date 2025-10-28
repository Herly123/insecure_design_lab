from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from code.secure import app as secure_app

app = FastAPI(title="Secure Auth API", version="1.0")

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(req: LoginRequest):
    ok = secure_app.login(req.username, req.password)
    if ok:
        return {"status": "ok", "message": "Acceso concedido"}
    else:
        raise HTTPException(status_code=401, detail="Acceso denegado o cuenta bloqueada")

@app.post("/admin/unlock/{username}", tags=["admin"])
def admin_unlock(username: str):
    """
    Desbloquea un usuario bloqueado.
    """
    try:
        secure_app._reset_user(username)
        return {"status": "ok", "message": f"Usuario '{username}' desbloqueado"}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Usuario '{username}' no encontrado")

@app.get("/health")
def health():
    return {"status": "running"}

