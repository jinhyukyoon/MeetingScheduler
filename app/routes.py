from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Reservation, CalendarSettings
from app.calendar import create_event
import datetime
import logging

logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    available_slots = CalendarSettings.query.all()
    return render_template('index.html', slots=available_slots)

@app.route('/reserve', methods=['POST'])
def reserve():
    name = request.form['name']
    phone = request.form['phone']
    password = request.form['password']
    datetime_str = request.form['datetime']
    
    try:
        reservation_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
    except ValueError as e:
        logging.error(f"Date format error: {e}")
        flash('Invalid datetime format.')
        return redirect(url_for('index'))

    reservation = Reservation(name=name, phone=phone, password=password, datetime=reservation_datetime, status='reserved')
    db.session.add(reservation)
    db.session.commit()

    # Create event in Google Calendar
    event = create_event(name, reservation_datetime.isoformat(), (reservation_datetime + datetime.timedelta(hours=1)).isoformat())
    if event:
        logging.info(f"Reservation event created: {event.get('htmlLink')}")
    else:
        logging.error("Failed to create reservation event.")
        flash('Failed to create calendar event.')
        return redirect(url_for('index'))

    # Send SMS to user
    # try:
    #     send_sms(phone, f'Reservation confirmed for {datetime_str}')
    # except Exception as e:
    #     logging.error(f"Error sending SMS: {e}")

    # TODO: Send KakaoTalk message to admin

    flash('Reservation successful!')
    return redirect(url_for('index'))

@app.route('/cancel', methods=['POST'])
def cancel():
    reservation_id = request.form['reservation_id']
    password = request.form['password']
    reservation = Reservation.query.get(reservation_id)

    if reservation and reservation.password == password:
        reservation.status = 'canceled'
        db.session.commit()

        # Send SMS to user
        # try:
        #     send_sms(reservation.phone, 'Your reservation has been canceled.')
        # except Exception as e:
        #     logging.error(f"Error sending SMS: {e}")

        # TODO: Send KakaoTalk message to admin

        flash('Reservation canceled.')
    else:
        flash('Invalid reservation or password.')

    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    reservations = Reservation.query.all()
    return render_template('admin.html', reservations=reservations)

@app.route('/admin/settings', methods=['POST'])
def admin_settings():
    available_date = request.form['available_date']
    available_time = request.form['available_time']

    calendar_setting = CalendarSettings(available_date=available_date, available_time=available_time)
    db.session.add(calendar_setting)
    db.session.commit()

    flash('Calendar settings updated.')
    return redirect(url_for('admin'))

@app.route('/admin/cancel', methods=['POST'])
def admin_cancel():
    reservation_id = request.form['reservation_id']
    reservation = Reservation.query.get(reservation_id)
    if reservation:
        reservation.status = 'canceled'
        db.session.commit()

        # TODO: Send SMS to user and KakaoTalk message to admin

        flash('Reservation canceled.')
    else:
        flash('Invalid reservation.')

    return redirect(url_for('admin'))
