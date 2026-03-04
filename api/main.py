from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from routes import users, products, carts

# TODO: Crear la instancia de FastAPI
app = FastAPI(title="Tienda Virtual API", version="1.0.0")

# TODO: Configurar CORS
app.add_middleware(
    CORSMiddleware,
    # TODO: Configurar orígenes permitidos, métodos, etc.
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: Incluir los routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(carts.router, prefix="/api/v1/carts", tags=["carts"])

@app.get("/")
async def root():
    # TODO: Endpoint de prueba
    return {"message": "Tienda Virtual API"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    # TODO: Endpoint de verificación de salud
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(exc)}"
        )