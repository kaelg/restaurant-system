import uvicorn
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from config.db.connection import get_db
from models.reservations import Reservation, ReservationStatus
from schemas.reservations import ReservationCreate, ReservationResponse, ReservationUpdate

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

def not_found_exception(db_item):
    """Helper function to raise 404 if item not found"""
    if db_item is None:
        raise HTTPException(status_code=404, detail="Reservation not found")


@app.get("/")
def root():
    return {"message": "Reservations API is running!"}


@app.get("/reservations", response_model=List[ReservationResponse])
def get_all_reservations(db: Session = Depends(get_db)):
    reservations = db.query(Reservation).all()
    return reservations


@app.post("/reservations", response_model=ReservationResponse)
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    new_reservation = Reservation(
        customer_name=reservation.customer_name,
        customer_phone=reservation.customer_phone,
        table_number=reservation.table_number,
        reservation_date=reservation.reservation_date,
        reservation_time=reservation.reservation_time,
        guests_count=reservation.guests_count
    )
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    return new_reservation


@app.get("/reservations/{reservation_id}", response_model=ReservationResponse)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    not_found_exception(reservation)
    return reservation


@app.put("/reservations/{reservation_id}", response_model=ReservationResponse)
def update_reservation(reservation_id: int, reservation_update: ReservationUpdate, db: Session = Depends(get_db)):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    not_found_exception(db_reservation)

    if reservation_update.customer_name is not None:
        db_reservation.customer_name = reservation_update.customer_name
    if reservation_update.customer_phone is not None:
        db_reservation.customer_phone = reservation_update.customer_phone
    if reservation_update.table_number is not None:
        db_reservation.table_number = reservation_update.table_number
    if reservation_update.reservation_date is not None:
        db_reservation.reservation_date = reservation_update.reservation_date
    if reservation_update.reservation_time is not None:
        db_reservation.reservation_time = reservation_update.reservation_time
    if reservation_update.guests_count is not None:
        db_reservation.guests_count = reservation_update.guests_count
    if reservation_update.status is not None:
        db_reservation.status = reservation_update.status.value

    db.commit()
    db.refresh(db_reservation)
    return db_reservation


@app.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    not_found_exception(db_reservation)

    db.delete(db_reservation)
    db.commit()
    return {"id": reservation_id, "message": "Reservation deleted successfully"}


@app.get("/reservations/date/{date}", response_model=List[ReservationResponse])
def get_reservations_by_date(date: str, db: Session = Depends(get_db)):
    reservations = db.query(Reservation).filter(Reservation.reservation_date == date).all()
    return reservations


@app.get("/reservations/table/{table_number}", response_model=List[ReservationResponse])
def get_reservations_by_table(table_number: int, db: Session = Depends(get_db)):
    reservations = db.query(Reservation).filter(Reservation.table_number == table_number).all()
    return reservations


@app.get("/reservations/status/{status}", response_model=List[ReservationResponse])
def get_reservations_by_status(status: ReservationStatus, db: Session = Depends(get_db)):
    reservations = db.query(Reservation).filter(Reservation.status == status.value).all()
    return reservations


@app.patch("/reservations/{reservation_id}/confirm")
def confirm_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    not_found_exception(reservation)

    if reservation.status == ReservationStatus.CONFIRMED.value:
        raise HTTPException(status_code=400, detail="Reservation is already confirmed")

    reservation.status = ReservationStatus.CONFIRMED.value
    db.commit()
    db.refresh(reservation)
    return {"id": reservation_id, "message": "Reservation confirmed", "status": reservation.status}


@app.patch("/reservations/{reservation_id}/cancel")
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    not_found_exception(reservation)

    if reservation.status == ReservationStatus.CANCELLED.value:
        raise HTTPException(status_code=400, detail="Reservation is already cancelled")

    reservation.status = ReservationStatus.CANCELLED.value
    db.commit()
    db.refresh(reservation)
    return {"id": reservation_id, "message": "Reservation cancelled", "status": reservation.status}


@app.patch("/reservations/{reservation_id}/complete")
def complete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    not_found_exception(reservation)

    if reservation.status == ReservationStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Reservation is already completed")

    reservation.status = ReservationStatus.COMPLETED.value
    db.commit()
    db.refresh(reservation)
    return {"id": reservation_id, "message": "Reservation completed", "status": reservation.status}


@app.get("/reservations/today", response_model=List[ReservationResponse])
def get_today_reservations(db: Session = Depends(get_db)):
    today = datetime.now().strftime("%Y-%m-%d")
    reservations = db.query(Reservation).filter(Reservation.reservation_date == today).all()
    return reservations



@app.get("/tables/availability/{date}")
def check_table_availability(date: str, db: Session = Depends(get_db)):
    reservations = db.query(Reservation).filter(
        Reservation.reservation_date == date,
        Reservation.status != ReservationStatus.CANCELLED.value
    ).all()

    occupied_tables = []
    for reservation in reservations:
        occupied_tables.append({
            "table_number": reservation.table_number,
            "time": reservation.reservation_time,
            "guests": reservation.guests_count,
            "status": reservation.status
        })

    return {
        "date": date,
        "occupied_tables": occupied_tables,
        "total_reservations": len(reservations)
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)