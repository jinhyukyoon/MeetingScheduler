from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import CalendarSettings, Reservation
from app.calendar import create_event, delete_event
import datetime
import logging

logging.basicConfig(level=logging.INFO)

from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import CalendarSettings, Reservation
from app.calendar import create_event, delete_event
import datetime
import logging

@app.route('/')
def index():
    available_slots = CalendarSettings.query.all()
    slots_by_date = {}
    for slot in available_slots:
        date_str = slot.available_date.strftime('%Y-%m-%d')
        if date_str not in slots_by_date:
            slots_by_date[date_str] = []
        reservation = Reservation.query.filter_by(datetime=datetime.datetime.combine(slot.available_date, slot.available_time), status='reserved').first()
        slots_by_date[date_str].append({
            'time': slot.available_time.strftime('%H:%M:%S'),
            'reserved': reservation is not None,
            'name': reservation.name if reservation else None,
            'phone': reservation.phone if reservation else None,
            'reservation_id': reservation.id if reservation else None
        })
    return render_template('index.html', slots=slots_by_date, is_admin=False)

@app.route('/reserve', methods=['POST'])
def reserve():
    name = request.form['name']
    phone = request.form['phone']
    password = request.form['password']
    datetime_str = request.form['datetime']
    
    try:
        reservation_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
    except ValueError as e:
        logging.error(f"Date format error: {e}")
        flash('Invalid datetime format.')
        return redirect(url_for('index'))

    # Check if the slot is still available
    existing_reservation = Reservation.query.filter_by(datetime=reservation_datetime, status='reserved').first()
    if existing_reservation:
        flash('This slot is already reserved.')
        return redirect(url_for('index'))

    # Continue with reservation creation
    try:
        reservation = Reservation(name=name, phone=phone, password=password, datetime=reservation_datetime, status='reserved')
        db.session.add(reservation)
        db.session.commit()
        
        # Update the slot to show it is reserved
        slot_to_update = CalendarSettings.query.filter_by(available_date=reservation_datetime.date(), available_time=reservation_datetime.time()).first()
        if slot_to_update:
            slot_to_update.reserved = True
            db.session.commit()

        # Create event in Google Calendar
        event = create_event(name, reservation_datetime.isoformat(), (reservation_datetime + datetime.timedelta(hours=1)).isoformat())
        if event:
            logging.info(f"Reservation event created: {event.get('htmlLink')}")
            reservation.event_id = event.get('id')  # Store the event ID
            db.session.commit()
            flash('Reservation successful!')
        else:
            logging.error("Failed to create reservation event.")
            flash('Failed to create calendar event.')
            return redirect(url_for('index'))

        # # Send SMS to user
        # try:
        #     send_sms(phone, f'Reservation confirmed for {datetime_str}')
        # except Exception as e:
        #     logging.error(f"Error sending SMS: {e}")

        # TODO: Send KakaoTalk message to admin

    except Exception as e:
        logging.error(f"Error creating reservation: {e}")
        flash('An error occurred while creating the reservation.')
        db.session.rollback()
    
    return redirect(url_for('index'))

@app.route('/cancel', methods=['POST'])
def cancel():
    reservation_id = request.form['reservation_id']
    phone = request.form['phone']
    password = request.form['password']
    reservation = Reservation.query.get(reservation_id)

    if reservation and reservation.phone == phone and reservation.password == password:
        reservation.status = 'canceled'
        reservation.canceled_at = datetime.datetime.utcnow()
        reservation.canceled_by = 'user'
        db.session.commit()

        # Delete the event from Google Calendar
        if reservation.event_id:
            delete_event(reservation.event_id)
        
        # Update the slot to show it is available again
        slot_to_update = CalendarSettings.query.filter_by(available_date=reservation.datetime.date(), available_time=reservation.datetime.time()).first()
        if slot_to_update:
            slot_to_update.reserved = False
            db.session.commit()

        # # Send SMS to user
        # try:
        #     send_sms(reservation.phone, 'Your reservation has been canceled.')
        # except Exception as e:
        #     logging.error(f"Error sending SMS: {e}")

        # TODO: Send KakaoTalk message to admin

        flash('Reservation canceled.')
    else:
        flash('Invalid phone number or password.')

    return redirect(url_for('index'))
