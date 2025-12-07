import requests
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.orders import CustomerOrder, RestaurantOrderUpdate, StatusUpdate
from models.orders import RestaurantOrder

def get_order_by_id(db: Session, order_id: int):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404,
                            detail="Menu item not found")

def get_all_orders(db: Session):
    orders = db.query(RestaurantOrder).all()
    return orders

def get_ready_not_delivered_orders(db: Session):
    orders = db.query(RestaurantOrder).filter((RestaurantOrder.ready == True) & (RestaurantOrder.delivered == False)).all()
    return orders

def get_not_ready_orders(db: Session):
    orders = db.query(RestaurantOrder).filter(RestaurantOrder.ready == False).all()
    return orders

def get_delivered_orders(db: Session):
    orders = db.query(RestaurantOrder).filter(RestaurantOrder.delivered == True).all()
    return orders

def create_order(db: Session, order: CustomerOrder):
    db_order = RestaurantOrder(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        status="nowe",
        items=order.items,
        total_price=order.total_price,
        ready=False,
        delivered=False,
        order_type=order.order_type.value,
        table_number=order.table_number,
        delivery_address=order.delivery_address
    )
    db.add(db_order)

    db.commit()
    db.refresh(db_order)
    return {"id": db_order.id,
            "status": "Order placed!"}

def create_task_from_order(db: Session, order_id: int):
    order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != "nowe":
        raise HTTPException(status_code=400, detail="Tasks already created")

    task_data = {
        "title": f"Przygotuj zamówienie #{order_id}",
        "description": f"Items: {order.items}",
        "staff_type": "kucharz",
        "assigned_to": None,
        "order_id": order_id,
        "order_type": order.order_type,
        "parent_task_id": None
    }

    try:
        response = requests.post("http://localhost:8001/tasks", json=task_data)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to create task")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Cannot connect to Tasks API")

    order.status = "w_przygotowaniu"
    db.commit()
    db.refresh(order)

    return {
        "message": "Tasks created successfully",
        "order_id": order_id,
        "task_created": response.json()
    }

def update_order(db: Session, order_id: int, new_order: RestaurantOrderUpdate):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db_order.customer_name = new_order.customer_name
    db_order.customer_phone = new_order.customer_phone
    db_order.status = new_order.status
    db_order.items = new_order.items
    db_order.total_price = new_order.total_price
    db_order.ready = new_order.ready
    db_order.delivered = new_order.delivered

    db.commit()
    db.refresh(db_order)
    return {"id": db_order.id,
            "status": "Order updated!  ",
            "New order": new_order}

def delete_order(db: Session, order_id: int):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(db_order)
    db.commit()
    return {"id": db_order.id, "Order": "deleted"}

def mark_ready(db: Session, order_id: int):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    if db_order.ready is True:
        raise HTTPException(status_code=406,
                            detail="Order was already marked as ready")
    db_order.ready = True

    db.commit()
    db.refresh(db_order)
    return {"id": order_id,
            "ready": True,
            "message": "Order marked as ready"}

def mark_delivered(db: Session, order_id: int):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if db_order.ready is False:
        raise HTTPException(status_code=403,
                            detail="You are trying to deliver not finished order!")
    if db_order.delivered is True:
        raise HTTPException(status_code=406,
                            detail="Order was already marked as delivered")
    db_order.delivered = True

    db.commit()
    db.refresh(db_order)
    return {"id": order_id,
            "delivered": True,
            "message": "Order marked as delivered"}




def change_order_status(db: Session, order_id: int, status_update: StatusUpdate):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if db_order.status == status_update.new_status.value:
        raise HTTPException(status_code=406,
                            detail=f"Order already has status: {status_update.new_status.value}")

    db_order.status = status_update.new_status.value
    db.commit()
    db.refresh(db_order)
    return {"id": order_id,
            "message": "Order status changed",
            "new_status": status_update.new_status.value}