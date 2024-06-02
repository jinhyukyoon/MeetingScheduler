from app import db

class CalendarSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    available_date = db.Column(db.Date, nullable=False)
    available_time = db.Column(db.Time, nullable=False)
    reserved = db.Column(db.Boolean, default=False)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='reserved')
    event_id = db.Column(db.String(256), nullable=True)
    canceled_at = db.Column(db.DateTime, nullable=True)
    canceled_by = db.Column(db.String(20), nullable=True)
