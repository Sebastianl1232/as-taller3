from fastapi import APIRouter, Depends, HTTPException, status, Body
from uuid import UUID
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product

router = APIRouter()

@router.get("/")
async def get_products(db: Session = Depends(get_db)):
    # TODO: Implementar obtener lista de productos
    products = db.query(Product).all()
    return [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price),
            "stock": product.stock,
            "image_url": product.image_url,
            "created_at": product.created_at,
        }
        for product in products
    ]

@router.get("/{product_id}")
async def get_product(product_id: UUID, db: Session = Depends(get_db)):
    # TODO: Implementar obtener producto por ID
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": float(product.price),
        "stock": product.stock,
        "image_url": product.image_url,
        "created_at": product.created_at,
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Body(...),
    description: str | None = Body(None),
    price: float = Body(...),
    stock: int = Body(0),
    image_url: str | None = Body(None),
    db: Session = Depends(get_db),
):
    # TODO: Implementar crear producto (admin)
    if price < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El precio no puede ser negativo")
    if stock < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El stock no puede ser negativo")

    product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_url=image_url,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    return {
        "message": "Producto creado exitosamente",
        "product": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price),
            "stock": product.stock,
            "image_url": product.image_url,
        },
    }

@router.put("/{product_id}")
async def update_product(
    product_id: UUID,
    name: str | None = Body(None),
    description: str | None = Body(None),
    price: float | None = Body(None),
    stock: int | None = Body(None),
    image_url: str | None = Body(None),
    db: Session = Depends(get_db),
):
    # TODO: Implementar actualizar producto
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        if price < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El precio no puede ser negativo")
        product.price = price
    if stock is not None:
        if stock < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El stock no puede ser negativo")
        product.stock = stock
    if image_url is not None:
        product.image_url = image_url

    db.commit()
    db.refresh(product)

    return {
        "message": "Producto actualizado",
        "product": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price),
            "stock": product.stock,
            "image_url": product.image_url,
        },
    }

@router.delete("/{product_id}")
async def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    # TODO: Implementar eliminar producto
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    db.delete(product)
    db.commit()
    return {"message": "Producto eliminado"}