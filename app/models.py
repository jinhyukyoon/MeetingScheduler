from app import db

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(128))
    datetime = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(20))

class CalendarSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    available_date = db.Column(db.Date, index=True)
    available_time = db.Column(db.Time, index=True)
