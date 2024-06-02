from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import CalendarSettings, Reservation
from app.google_calendar import delete_google_calendar_event
import datetime, logging

logging.basicConfig(level=logging.INFO)

@app.route('/admin')
def admin():
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
            'reservation_id': reservation.id if reservation else None,
            'slot_id': slot.id
        })
    return render_template('admin.html', slots=slots_by_date, is_admin=True)

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
            delete_google_calendar_event(reservation.event_id)

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
