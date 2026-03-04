from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from uuid import UUID
from sqlalchemy.orm import Session
from database import get_db
from models.carts import Cart, CartItem
from models.product import Product
from models.user import User

router = APIRouter()

def _get_or_create_cart(db: Session, user_id: UUID) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

@router.get("/")
async def get_user_cart(user_id: UUID = Query(...), db: Session = Depends(get_db)):
    # TODO: Implementar obtener carrito del usuario
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    cart = _get_or_create_cart(db, user_id)
    items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

    response_items = []
    total = 0.0
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue
        subtotal = float(product.price) * item.quantity
        total += subtotal
        response_items.append(
            {
                "item_id": item.id,
                "product_id": product.id,
                "name": product.name,
                "price": float(product.price),
                "quantity": item.quantity,
                "subtotal": subtotal,
            }
        )

    return {
        "cart_id": cart.id,
        "user_id": cart.user_id,
        "items": response_items,
        "total": total,
    }

@router.post("/items")
async def add_item_to_cart(
    user_id: UUID = Body(...),
    product_id: UUID = Body(...),
    quantity: int = Body(1),
    db: Session = Depends(get_db),
):
    # TODO: Implementar agregar item al carrito
    if quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad debe ser mayor que cero")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    cart = _get_or_create_cart(db, user_id)
    item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()

    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(item)

    db.commit()
    db.refresh(item)

    return {
        "message": "Item agregado al carrito",
        "item": {
            "id": item.id,
            "cart_id": item.cart_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
        },
    }

@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: UUID,
    quantity: int = Body(...),
    db: Session = Depends(get_db),
):
    # TODO: Implementar actualizar cantidad de item
    if quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad debe ser mayor que cero")

    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")

    item.quantity = quantity
    db.commit()
    db.refresh(item)

    return {
        "message": "Cantidad actualizada",
        "item": {
            "id": item.id,
            "cart_id": item.cart_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
        },
    }

@router.delete("/items/{item_id}")
async def remove_item_from_cart(item_id: UUID, db: Session = Depends(get_db)):
    # TODO: Implementar remover item del carrito
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")

    db.delete(item)
    db.commit()
    return {"message": "Item removido del carrito"}

@router.delete("/")
async def clear_cart(user_id: UUID = Query(...), db: Session = Depends(get_db)):
    # TODO: Implementar limpiar carrito
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete(synchronize_session=False)
    db.commit()
    return {"message": "Carrito limpiado"}
