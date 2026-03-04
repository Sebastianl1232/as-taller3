from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from database import get_db
from models.user import User

router = APIRouter()

@router.post("/register")
async def register_user(
    username: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db),
):
    # TODO: Implementar registro de usuario
    existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username o email ya registrado",
        )

    user = User(username=username, email=email, password_hash=password, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Usuario registrado exitosamente",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
        },
    }

@router.post("/login")  
async def login_user(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db),
):
    # TODO: Implementar login de usuario
    user = db.query(User).filter(User.email == email).first()
    if not user or user.password_hash != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    return {
        "message": "Login exitoso",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }

@router.get("/profile")
async def get_user_profile(
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    # TODO: Implementar obtener perfil de usuario
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }

@router.put("/profile")
async def update_user_profile(
    user_id: int = Body(...),
    username: str | None = Body(None),
    email: str | None = Body(None),
    password: str | None = Body(None),
    is_active: bool | None = Body(None),
    db: Session = Depends(get_db),
):
    # TODO: Implementar actualizar perfil de usuario
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if username and username != user.username:
        username_exists = db.query(User).filter(User.username == username, User.id != user.id).first()
        if username_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username ya en uso")
        user.username = username

    if email and email != user.email:
        email_exists = db.query(User).filter(User.email == email, User.id != user.id).first()
        if email_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya en uso")
        user.email = email

    if password:
        user.password_hash = password

    if is_active is not None:
        user.is_active = is_active

    db.commit()
    db.refresh(user)

    return {
        "message": "Perfil actualizado",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
        },
    }