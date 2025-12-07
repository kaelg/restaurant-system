import requests
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from models.reservations import Reservation, ReservationStatus
from schemas.reservations import ReservationCreate, ReservationUpdate


def get_all_reservaions(db: Session):
    db_reservations = db.query(Reservation).all()
    return db_reservations


def get_reservation_by_id(db: Session, reservation_id: int):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404,
                            detail="Menu item not found")


def create_reservation(db: Session, reservation: ReservationCreate):
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


def update_reservation(db: Session, reservation_id: int, reservation_update: ReservationUpdate):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

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


def delete_reservation(db: Session, reservation_id: int):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    db.delete(db_reservation)
    db.commit()
    return {"id": reservation_id, "message": "Reservation deleted successfully"}


def get_reservation_by_date(db: Session, date: str):
    reservations = db.query(Reservation).filter(Reservation.reservation_date == date).all()
    return reservations


def get_reservation_by_table(db: Session, table_number: int):
    reservations = db.query(Reservation).filter(Reservation.table_number == table_number).all()
    return reservations


def get_reservation_by_status(db: Session, status: ReservationStatus):
    reservations = db.query(Reservation).filter(Reservation.status == status.value).all()
    return reservations


def confirm_reservation(db: Session, reservation_id: int):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if db_reservation.status == ReservationStatus.CONFIRMED.value:
        raise HTTPException(status_code=400, detail="Reservation is already confirmed")

    db_reservation.status = ReservationStatus.CONFIRMED.value
    db.commit()
    db.refresh(db_reservation)
    return {"id": reservation_id, "message": "Reservation confirmed", "status": db_reservation.status}


def cancel_reservation(db: Session, reservation_id: int):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if db_reservation.status == ReservationStatus.CANCELLED.value:
        raise HTTPException(status_code=400, detail="Reservation is already cancelled")

    db_reservation.status = ReservationStatus.CANCELLED.value
    db.commit()
    db.refresh(db_reservation)
    return {"id": reservation_id, "message": "Reservation cancelled", "status": db_reservation.status}
