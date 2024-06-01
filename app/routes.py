from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Reservation, CalendarSettings
from app.calendar import create_event, delete_event
# from sms_api import send_sms
import datetime
import logging

logging.basicConfig(level=logging.INFO)

@app.route('/admin/delete_slot', methods=['POST'])
def admin_delete_slot():
    slot_id = request.form['slot_id']
    slot = CalendarSettings.query.get(slot_id)
    if slot:
        db.session.delete(slot)
        db.session.commit()
        flash('Available slot deleted.')
    else:
        flash('Invalid slot.')
    return redirect(url_for('admin'))

@app.route('/')
def index():
    available_slots = CalendarSettings.query.all()
    slots_by_year_month = {}
    for slot in available_slots:
        year_month = slot.available_date.strftime('%Y-%m')
        if year_month not in slots_by_year_month:
            slots_by_year_month[year_month] = []
        reservation = Reservation.query.filter_by(datetime=datetime.datetime.combine(slot.available_date, slot.available_time), status='reserved').first()
        slot.reserved = reservation is not None
        slots_by_year_month[year_month].append(slot)
    return render_template('index.html', slots_by_year_month=slots_by_year_month)

@app.route('/admin')
def admin():
    available_slots = CalendarSettings.query.all()
    slots_by_year_month = {}
    for slot in available_slots:
        year_month = slot.available_date.strftime('%Y-%m')
        if year_month not in slots_by_year_month:
            slots_by_year_month[year_month] = []
        reservation = Reservation.query.filter_by(datetime=datetime.datetime.combine(slot.available_date, slot.available_time), status='reserved').first()
        slot.reserved = reservation is not None
        slots_by_year_month[year_month].append(slot)
    reservations = Reservation.query.all()
    return render_template('admin.html', reservations=reservations, slots_by_year_month=slots_by_year_month, is_admin=True)

@app.route('/admin/settings', methods=['POST'])
def admin_settings():
    available_date = request.form['available_date']
    available_time = request.form['available_time']
    repeat = request.form['repeat']
    end_date_str = request.form['end_date']

    try:
        start_date = datetime.datetime.strptime(available_date, '%Y-%m-%d').date()
        time = datetime.datetime.strptime(available_time, '%H:%M').time()
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    except ValueError as e:
        logging.error(f"Date format error: {e}")
        flash('Invalid date format.')
        return redirect(url_for('admin'))

    if repeat != 'none' and not end_date:
        flash('Please provide an end date for the repetition.')
        return redirect(url_for('admin'))

    current_date = start_date

    while True:
        if repeat == 'daily' and current_date.weekday() >= 5:  # Skip weekends
            current_date += datetime.timedelta(days=1)
            continue

        calendar_setting = CalendarSettings(available_date=current_date, available_time=time)
        db.session.add(calendar_setting)
        
        if repeat == 'none':
            break
        elif repeat == 'daily':
            current_date += datetime.timedelta(days=1)
        elif repeat == 'weekly':
            current_date += datetime.timedelta(weeks=1)
        elif repeat == 'monthly':
            current_date = (current_date.replace(day=1) + datetime.timedelta(days=32)).replace(day=current_date.day)

        if end_date and current_date > end_date:
            break

    db.session.commit()
    flash('Calendar settings updated.')
    return redirect(url_for('admin'))

@app.route('/admin/cancel', methods=['POST'])
def admin_cancel():
    reservation_id = request.form['reservation_id']
    reservation = Reservation.query.get(reservation_id)
    if reservation:
        reservation.status = 'canceled'
        reservation.canceled_at = datetime.datetime.utcnow()
        reservation.canceled_by = 'admin'
        db.session.commit()

        # Delete the event from Google Calendar
        if reservation.event_id:
            delete_event(reservation.event_id)

        # # Send SMS to user
        # try:
        #     send_sms(reservation.phone, 'Your reservation has been canceled by admin.')
        # except Exception as e:
        #     logging.error(f"Error sending SMS: {e}")

        # TODO: Send KakaoTalk message to admin

        flash('Reservation canceled.')
    else:
        flash('Invalid reservation.')

    return redirect(url_for('admin'))

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
    password = request.form['password']
    reservation = Reservation.query.get(reservation_id)

    if reservation and reservation.password == password:
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
        flash('Invalid reservation or password.')

    return redirect(url_for('index'))
