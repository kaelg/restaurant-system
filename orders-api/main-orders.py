import requests
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config.db.connection import get_db
from models.orders import RestaurantOrder
from schemas.orders import CustomerOrder, RestaurantOrderUpdate, StatusUpdate
from services import orders_service

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
    return orders_service.get_order_by_id(db, order_id)


@app.get("/restaurant_orders/all_orders")
def get_all_orders(db: Session = Depends(get_db)):
    return orders_service.get_all_orders(db)


@app.get("/restaurant_orders/ready_not_delivered_orders")
def get_ready_not_delivered_orders(db: Session = Depends(get_db)):
    return orders_service.get_ready_not_delivered_orders(db)


@app.get("/restaurant_orders/not_ready_orders")
def get_not_ready_orders(db: Session = Depends(get_db)):
    return orders_service.get_not_ready_orders(db)


@app.get("/restaurant_orders/delivered_orders")
def get_delivered_orders(db: Session = Depends(get_db)):
    return orders_service.get_delivered_orders(db)


@app.post("/restaurant_orders/place_order/")
def place_order(customer_order: CustomerOrder, db: Session = Depends(get_db)):
    return orders_service.create_order(db, customer_order)


@app.post("/restaurant_orders/{order_id}/create_tasks")
def create_tasks_from_order(order_id: int, db: Session = Depends(get_db)):
    return orders_service.create_task_from_order(db, order_id)

@app.put("/restaurant_orders/{order_id}")
def update_order(order_id: int, new_order: RestaurantOrderUpdate, db: Session = Depends(get_db)):
    return orders_service.update_order(db, order_id, new_order)


@app.delete("/restaurant_orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    return orders_service.delete_order(db, order_id)


@app.patch("/restaurant_orders/mark_ready/{order_id}")
def mark_ready(order_id: int, db: Session = Depends(get_db)):
    return orders_service.mark_ready(db, order_id)


@app.patch("/restaurant_orders/mark_delivered/{order_id}")
def mark_delivered(order_id: int, db: Session = Depends(get_db)):
    return orders_service.mark_delivered(db, order_id)


@app.patch("/restaurant_orders/change_status/{order_id}")
def change_order_status(order_id: int, status_update: StatusUpdate, db: Session = Depends(get_db)):
    return orders_service.change_order_status(db, order_id, status_update)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)