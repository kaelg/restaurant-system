import uvicorn
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from config.db.connection import get_db
from models.reservations import Reservation, ReservationStatus
from schemas.reservations import ReservationCreate, ReservationResponse, ReservationUpdate
from services import reservations_service
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


@app.get("/reservations/{reservation_id}", response_model=ReservationResponse)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    return reservations_service.get_reservation_by_id(db, reservation_id)


@app.get("/reservations", response_model=List[ReservationResponse])
def get_all_reservations(db: Session = Depends(get_db)):
    return reservations_service.get_all_reservaions(db)


@app.post("/reservations", response_model=ReservationResponse)
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    return reservations_service.create_reservation(db, reservation)


@app.put("/reservations/{reservation_id}", response_model=ReservationResponse)
def update_reservation(reservation_id: int, reservation_update: ReservationUpdate, db: Session = Depends(get_db)):
    return reservations_service.update_reservation(db, reservation_id, reservation_update)


@app.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    return reservations_service.delete_reservation(db, reservation_id)


@app.get("/reservations/date/{date}", response_model=List[ReservationResponse])
def get_reservations_by_date(date: str, db: Session = Depends(get_db)):
    return reservations_service.get_reservation_by_date(db, date)


@app.get("/reservations/table/{table_number}", response_model=List[ReservationResponse])
def get_reservations_by_table(table_number: int, db: Session = Depends(get_db)):
    return reservations_service.get_reservation_by_table(db,table_number)


@app.get("/reservations/status/{status}", response_model=List[ReservationResponse])
def get_reservations_by_status(status: ReservationStatus, db: Session = Depends(get_db)):
    return reservations_service.get_reservation_by_status(db, status)


@app.patch("/reservations/{reservation_id}/confirm")
def confirm_reservation(reservation_id: int, db: Session = Depends(get_db)):
    return reservations_service.confirm_reservation(db, reservation_id)


@app.patch("/reservations/{reservation_id}/cancel")
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
   return reservations_service.cancel_reservation(db, reservation_id)

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