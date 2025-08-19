import requests
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config.db.connection import get_db
from models.orders import RestaurantOrder
from schemas.orders import CustomerOrder, RestaurantOrderUpdate, StatusUpdate

app = FastAPI()
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=['*'],
)

@app.get("/restaurant_orders/single_order/{order_id}")
def get_single_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    not_found_exception(db_order)
    return db_order


@app.get("/restaurant_orders/all_orders")
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(RestaurantOrder).all()
    return orders


@app.get("/restaurant_orders/ready_not_delivered_orders")
def get_ready_not_delivered_orders(db: Session = Depends(get_db)):
    orders = db.query(RestaurantOrder).filter((RestaurantOrder.ready == True) & (RestaurantOrder.delivered == False)).all()
    return orders


@app.get("/restaurant_orders/not_ready_orders")
def get_not_ready_orders(db: Session = Depends(get_db)):
    orders = db.query(RestaurantOrder).filter(RestaurantOrder.ready == False).all()
    return orders


@app.get("/restaurant_orders/delivered_orders")
def get_delivered_orders(db: Session = Depends(get_db)):
    orders = db.query(RestaurantOrder).filter(RestaurantOrder.delivered == True).all()
    return orders


@app.post("/restaurant_orders/place_order/")
def place_order(customer_order: CustomerOrder, db: Session = Depends(get_db)):
    db_order = RestaurantOrder(
        customer_name = customer_order.customer_name,
        customer_phone = customer_order.customer_phone,
        status = "nowe",
        items = customer_order.items,
        total_price = customer_order.total_price,
        ready = False,
        delivered = False,
        order_type = customer_order.order_type.value,
        table_number = customer_order.table_number,
        delivery_address = customer_order.delivery_address
    )
    db.add(db_order)

    db.commit()
    db.refresh(db_order)
    return {"id": db_order.id,
            "status": "Order placed!"}


@app.post("/restaurant_orders/{order_id}/create_tasks")
def create_tasks_from_order(order_id: int, db: Session = Depends(get_db)):
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




@app.put("/restaurant_orders/{order_id}")
def update_order(order_id: int, new_order: RestaurantOrderUpdate, db: Session = Depends(get_db)):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    if db_order is None:
        return "Order not found"
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


@app.delete("/restaurant_orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    not_found_exception(db_order)

    db.delete(db_order)
    db.commit()
    return {"id": db_order.id, "Order": "deleted"}


@app.patch("/restaurant_orders/mark_ready/{order_id}")
def mark_ready(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    not_found_exception(db_order)
    if db_order.ready is True:
        raise HTTPException(status_code=406,
                            detail="Order was already marked as ready")
    db_order.ready = True

    db.commit()
    db.refresh(db_order)
    return {"id": order_id,
            "ready": True,
            "message": "Order marked as ready"}


@app.patch("/restaurant_orders/mark_delivered/{order_id}")
def mark_delivered(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    not_found_exception(db_order)
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


@app.patch("/restaurant_orders/change_status/{order_id}")
def change_order_status(order_id: int, status_update: StatusUpdate, db: Session = Depends(get_db)):
    db_order = db.query(RestaurantOrder).filter(RestaurantOrder.id == order_id).first()
    not_found_exception(db_order)

    if db_order.status == status_update.new_status.value:
        raise HTTPException(status_code=406,
                            detail=f"Order already has status: {status_update.new_status.value}")

    db_order.status = status_update.new_status.value
    db.commit()
    db.refresh(db_order)
    return {"id": order_id,
            "message": "Order status changed",
            "new_status": status_update.new_status.value}


def not_found_exception(db_order: RestaurantOrder):
    if db_order is None:
        raise HTTPException(status_code=404,
                            detail="Order not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)